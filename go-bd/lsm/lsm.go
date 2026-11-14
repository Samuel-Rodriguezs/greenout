// Pacote lsm implementa uma LSM-tree simplificada: escritas vão para uma
// memtable; quando ela enche, é descarregada em uma SSTable imutável em
// arquivo; leituras consultam memtable e tabelas da mais nova para a mais
// antiga (usando um filtro de Bloom por tabela); a compactação funde todas
// as tabelas numa só e descarta lápides.
//
// Formato da SSTable:
//
//	registros: [flag u8 (1 = lápide)][klen uvarint][vlen uvarint][chave][valor] ...
//	bloom:     filtro serializado (pacote bloom)
//	rodapé:    [tamDados u64][tamBloom u64][quantidade u64][crc32 u32][magic u32]
//
// O CRC cobre registros + bloom. Arquivos de compactação se chamam
// "<lo>-<hi>.sst" e substituem as tabelas com ids em [lo, hi]; assim uma
// queda entre gravar o resultado e apagar as entradas antigas é desfeita
// na abertura seguinte.
package lsm

import (
	"encoding/binary"
	"errors"
	"fmt"
	"hash/crc32"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	"sync"
	"sync/atomic"

	"greenout/bd/bloom"
	"greenout/bd/iterador"
)

const (
	magic     uint32 = 0x4C534D31
	tamRodape        = 32
	// LimitePadrao é o tamanho da memtable (em bytes aproximados) que dispara o flush.
	LimitePadrao = 1 << 20
)

var (
	// ErrCorrompido indica SSTable com estrutura ou checksum inválidos.
	ErrCorrompido = errors.New("lsm: sstable corrompida")
	// ErrFechado indica uso do banco após Fechar.
	ErrFechado = errors.New("lsm: banco fechado")
)

// ---- codificação de registros ----

func codificar(dst []byte, e iterador.Entrada) []byte {
	var flag byte
	if e.Apagado {
		flag = 1
	}
	dst = append(dst, flag)
	dst = binary.AppendUvarint(dst, uint64(len(e.Chave)))
	dst = binary.AppendUvarint(dst, uint64(len(e.Valor)))
	dst = append(dst, e.Chave...)
	return append(dst, e.Valor...)
}

func decodificar(b []byte) (iterador.Entrada, int, error) {
	var e iterador.Entrada
	if len(b) < 1 || b[0] > 1 {
		return e, 0, ErrCorrompido
	}
	e.Apagado = b[0] == 1
	pos := 1
	kl, n := binary.Uvarint(b[pos:])
	if n <= 0 {
		return e, 0, ErrCorrompido
	}
	pos += n
	vl, n := binary.Uvarint(b[pos:])
	if n <= 0 {
		return e, 0, ErrCorrompido
	}
	pos += n
	resto := uint64(len(b) - pos)
	if kl > resto || vl > resto-kl || (e.Apagado && vl != 0) {
		return e, 0, ErrCorrompido
	}
	e.Chave = string(b[pos : pos+int(kl)])
	pos += int(kl)
	if vl > 0 {
		e.Valor = append([]byte(nil), b[pos:pos+int(vl)]...)
	}
	return e, pos + int(vl), nil
}

// ---- SSTable ----

type tabela struct {
	caminho string
	lo, hi  int
	f       *os.File
	chaves  []string
	offs    []int64 // offs[i] = início do registro i; offs[n] = fim dos dados
	filtro  *bloom.Filtro
}

func nomeTabela(lo, hi int) string {
	if lo == hi {
		return fmt.Sprintf("%08d.sst", lo)
	}
	return fmt.Sprintf("%08d-%08d.sst", lo, hi)
}

func escreverTabela(caminho string, es []iterador.Entrada) error {
	filtro, err := bloom.Novo(max(len(es), 1), 0.01)
	if err != nil {
		return err
	}
	var buf []byte
	for _, e := range es {
		filtro.Adicionar([]byte(e.Chave))
		buf = codificar(buf, e)
	}
	bl, err := filtro.MarshalBinary()
	if err != nil {
		return err
	}
	tamDados := len(buf)
	buf = append(buf, bl...)
	crc := crc32.ChecksumIEEE(buf)
	buf = binary.LittleEndian.AppendUint64(buf, uint64(tamDados))
	buf = binary.LittleEndian.AppendUint64(buf, uint64(len(bl)))
	buf = binary.LittleEndian.AppendUint64(buf, uint64(len(es)))
	buf = binary.LittleEndian.AppendUint32(buf, crc)
	buf = binary.LittleEndian.AppendUint32(buf, magic)

	tmp := caminho + ".tmp"
	f, err := os.OpenFile(tmp, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0o644)
	if err != nil {
		return err
	}
	if _, err := f.Write(buf); err != nil {
		f.Close()
		os.Remove(tmp)
		return err
	}
	if err := f.Sync(); err != nil {
		f.Close()
		os.Remove(tmp)
		return err
	}
	if err := f.Close(); err != nil {
		os.Remove(tmp)
		return err
	}
	return os.Rename(tmp, caminho)
}

func abrirTabela(caminho string, lo, hi int) (*tabela, error) {
	b, err := os.ReadFile(caminho)
	if err != nil {
		return nil, err
	}
	falha := func(motivo string) (*tabela, error) {
		return nil, fmt.Errorf("%w: %s: %s", ErrCorrompido, filepath.Base(caminho), motivo)
	}
	if len(b) < tamRodape {
		return falha("arquivo menor que o rodapé")
	}
	rod := b[len(b)-tamRodape:]
	if binary.LittleEndian.Uint32(rod[28:]) != magic {
		return falha("magic inválido")
	}
	tamDados := binary.LittleEndian.Uint64(rod[0:])
	tamBloom := binary.LittleEndian.Uint64(rod[8:])
	qtd := binary.LittleEndian.Uint64(rod[16:])
	corpo := uint64(len(b) - tamRodape)
	if tamDados > corpo || tamBloom != corpo-tamDados {
		return falha("tamanhos do rodapé inconsistentes")
	}
	if crc32.ChecksumIEEE(b[:corpo]) != binary.LittleEndian.Uint32(rod[24:]) {
		return falha("checksum divergente")
	}
	filtro, err := bloom.Carregar(b[tamDados:corpo])
	if err != nil {
		return falha("filtro de bloom inválido")
	}
	t := &tabela{caminho: caminho, lo: lo, hi: hi, filtro: filtro}
	dados := b[:tamDados]
	pos := 0
	for pos < len(dados) {
		e, n, err := decodificar(dados[pos:])
		if err != nil {
			return falha("registro inválido")
		}
		if len(t.chaves) > 0 && t.chaves[len(t.chaves)-1] >= e.Chave {
			return falha("chaves fora de ordem")
		}
		t.chaves = append(t.chaves, e.Chave)
		t.offs = append(t.offs, int64(pos))
		pos += n
	}
	t.offs = append(t.offs, int64(pos))
	if uint64(len(t.chaves)) != qtd {
		return falha("quantidade de registros diverge do rodapé")
	}
	if t.f, err = os.Open(caminho); err != nil {
		return nil, err
	}
	return t, nil
}

// obter procura a chave; evitadas conta leituras poupadas pelo Bloom.
func (t *tabela) obter(chave string, evitadas *atomic.Uint64) (iterador.Entrada, bool, error) {
	var vazio iterador.Entrada
	if !t.filtro.Possui([]byte(chave)) {
		evitadas.Add(1)
		return vazio, false, nil
	}
	i := sort.SearchStrings(t.chaves, chave)
	if i == len(t.chaves) || t.chaves[i] != chave {
		return vazio, false, nil
	}
	buf := make([]byte, t.offs[i+1]-t.offs[i])
	if _, err := t.f.ReadAt(buf, t.offs[i]); err != nil {
		return vazio, false, err
	}
	e, _, err := decodificar(buf)
	if err != nil || e.Chave != chave {
		return vazio, false, ErrCorrompido
	}
	return e, true, nil
}

func (t *tabela) todas() ([]iterador.Entrada, error) {
	buf := make([]byte, t.offs[len(t.offs)-1])
	if len(buf) > 0 {
		if _, err := t.f.ReadAt(buf, 0); err != nil {
			return nil, err
		}
	}
	es := make([]iterador.Entrada, 0, len(t.chaves))
	for len(buf) > 0 {
		e, n, err := decodificar(buf)
		if err != nil {
			return nil, err
		}
		es = append(es, e)
		buf = buf[n:]
	}
	return es, nil
}

// ---- banco ----

// Opcoes configura o banco.
type Opcoes struct {
	// LimiteMemtable é o tamanho aproximado, em bytes, que dispara o flush. Zero usa LimitePadrao.
	LimiteMemtable int
}

// Banco é a LSM-tree.
type Banco struct {
	mu       sync.RWMutex
	dir      string
	limite   int
	mem      map[string]iterador.Entrada
	memBytes int
	tabelas  []*tabela // da mais antiga para a mais nova
	proxID   int
	fechado  bool
	evitadas atomic.Uint64
}

// Abrir carrega as SSTables do diretório (criando-o se preciso), aplica
// resíduos de compactações interrompidas e valida cada tabela.
func Abrir(dir string, op Opcoes) (*Banco, error) {
	if err := os.MkdirAll(dir, 0o755); err != nil {
		return nil, err
	}
	ents, err := os.ReadDir(dir)
	if err != nil {
		return nil, err
	}
	type arq struct {
		nome   string
		lo, hi int
	}
	var arqs []arq
	for _, e := range ents {
		nome := e.Name()
		if e.IsDir() {
			continue
		}
		if strings.HasSuffix(nome, ".tmp") {
			os.Remove(filepath.Join(dir, nome))
			continue
		}
		base, ok := strings.CutSuffix(nome, ".sst")
		if !ok {
			continue
		}
		a, b, composto := strings.Cut(base, "-")
		lo, err1 := strconv.Atoi(a)
		hi := lo
		var err2 error
		if composto {
			hi, err2 = strconv.Atoi(b)
		}
		if err1 != nil || err2 != nil || lo > hi {
			return nil, fmt.Errorf("%w: nome inesperado %q", ErrCorrompido, nome)
		}
		arqs = append(arqs, arq{nome, lo, hi})
	}
	// descarta tabelas cobertas por um arquivo de compactação
	var vivos []arq
	for _, a := range arqs {
		coberta := false
		for _, o := range arqs {
			if o.nome != a.nome && o.lo <= a.lo && a.hi <= o.hi {
				coberta = true
				break
			}
		}
		if coberta {
			os.Remove(filepath.Join(dir, a.nome))
		} else {
			vivos = append(vivos, a)
		}
	}
	sort.Slice(vivos, func(i, j int) bool { return vivos[i].hi < vivos[j].hi })

	b := &Banco{dir: dir, limite: op.LimiteMemtable, mem: map[string]iterador.Entrada{}, proxID: 1}
	if b.limite <= 0 {
		b.limite = LimitePadrao
	}
	for _, a := range vivos {
		t, err := abrirTabela(filepath.Join(dir, a.nome), a.lo, a.hi)
		if err != nil {
			b.fecharTabelas()
			return nil, err
		}
		b.tabelas = append(b.tabelas, t)
		b.proxID = a.hi + 1
	}
	return b, nil
}

func (b *Banco) fecharTabelas() {
	for _, t := range b.tabelas {
		t.f.Close()
	}
	b.tabelas = nil
}

func tamanhoEntrada(e iterador.Entrada) int { return len(e.Chave) + len(e.Valor) + 16 }

func (b *Banco) gravarMem(e iterador.Entrada) error {
	if b.fechado {
		return ErrFechado
	}
	if antigo, ok := b.mem[e.Chave]; ok {
		b.memBytes -= tamanhoEntrada(antigo)
	}
	b.mem[e.Chave] = e
	b.memBytes += tamanhoEntrada(e)
	if b.memBytes >= b.limite {
		return b.descarregar()
	}
	return nil
}

// Definir grava chave=valor.
func (b *Banco) Definir(chave string, valor []byte) error {
	b.mu.Lock()
	defer b.mu.Unlock()
	return b.gravarMem(iterador.Entrada{Chave: chave, Valor: append([]byte(nil), valor...)})
}

// Remover grava uma lápide para a chave.
func (b *Banco) Remover(chave string) error {
	b.mu.Lock()
	defer b.mu.Unlock()
	return b.gravarMem(iterador.Entrada{Chave: chave, Apagado: true})
}

// Obter procura a chave na memtable e nas tabelas, da mais nova para a mais antiga.
func (b *Banco) Obter(chave string) ([]byte, bool, error) {
	b.mu.RLock()
	defer b.mu.RUnlock()
	if b.fechado {
		return nil, false, ErrFechado
	}
	if e, ok := b.mem[chave]; ok {
		return valorDe(e)
	}
	for i := len(b.tabelas) - 1; i >= 0; i-- {
		e, ok, err := b.tabelas[i].obter(chave, &b.evitadas)
		if err != nil {
			return nil, false, err
		}
		if ok {
			return valorDe(e)
		}
	}
	return nil, false, nil
}

func valorDe(e iterador.Entrada) ([]byte, bool, error) {
	if e.Apagado {
		return nil, false, nil
	}
	return append([]byte{}, e.Valor...), true, nil
}

// Descarregar força a gravação da memtable em uma nova SSTable.
func (b *Banco) Descarregar() error {
	b.mu.Lock()
	defer b.mu.Unlock()
	if b.fechado {
		return ErrFechado
	}
	return b.descarregar()
}

func (b *Banco) descarregar() error {
	if len(b.mem) == 0 {
		return nil
	}
	es := make([]iterador.Entrada, 0, len(b.mem))
	for _, e := range b.mem {
		es = append(es, e)
	}
	sort.Slice(es, func(i, j int) bool { return es[i].Chave < es[j].Chave })
	id := b.proxID
	caminho := filepath.Join(b.dir, nomeTabela(id, id))
	if err := escreverTabela(caminho, es); err != nil {
		return err
	}
	t, err := abrirTabela(caminho, id, id)
	if err != nil {
		return err
	}
	b.tabelas = append(b.tabelas, t)
	b.proxID++
	b.mem = map[string]iterador.Entrada{}
	b.memBytes = 0
	return nil
}

// Compactar funde todas as tabelas em uma só, descartando valores
// sobrescritos e lápides.
func (b *Banco) Compactar() error {
	b.mu.Lock()
	defer b.mu.Unlock()
	if b.fechado {
		return ErrFechado
	}
	if err := b.descarregar(); err != nil {
		return err
	}
	if len(b.tabelas) < 2 {
		return nil
	}
	fontes := make([]iterador.Iterador, 0, len(b.tabelas))
	for i := len(b.tabelas) - 1; i >= 0; i-- { // mais nova primeiro
		es, err := b.tabelas[i].todas()
		if err != nil {
			return err
		}
		fontes = append(fontes, iterador.DeSlice(es))
	}
	vivos, err := iterador.Coletar(iterador.SemApagados(iterador.Mesclar(fontes...)))
	if err != nil {
		return err
	}
	lo, hi := b.tabelas[0].lo, b.tabelas[len(b.tabelas)-1].hi
	caminho := filepath.Join(b.dir, nomeTabela(lo, hi))
	if err := escreverTabela(caminho, vivos); err != nil {
		return err
	}
	nova, err := abrirTabela(caminho, lo, hi)
	if err != nil {
		return err
	}
	for _, t := range b.tabelas {
		t.f.Close()
		os.Remove(t.caminho)
	}
	b.tabelas = []*tabela{nova}
	return nil
}

// Intervalo devolve as chaves vivas em [de, ate), em ordem. ate vazio
// significa sem limite superior.
func (b *Banco) Intervalo(de, ate string) ([]iterador.Entrada, error) {
	b.mu.RLock()
	defer b.mu.RUnlock()
	if b.fechado {
		return nil, ErrFechado
	}
	mem := make([]iterador.Entrada, 0, len(b.mem))
	for _, e := range b.mem {
		mem = append(mem, e)
	}
	sort.Slice(mem, func(i, j int) bool { return mem[i].Chave < mem[j].Chave })
	fontes := []iterador.Iterador{iterador.DeSlice(mem)}
	for i := len(b.tabelas) - 1; i >= 0; i-- {
		es, err := b.tabelas[i].todas()
		if err != nil {
			return nil, err
		}
		fontes = append(fontes, iterador.DeSlice(es))
	}
	it := iterador.SemApagados(iterador.Intervalo(iterador.Mesclar(fontes...), de, ate, ate == ""))
	res, err := iterador.Coletar(it)
	for i := range res {
		res[i].Valor = append([]byte{}, res[i].Valor...)
	}
	return res, err
}

// NumTabelas devolve quantas SSTables existem.
func (b *Banco) NumTabelas() int {
	b.mu.RLock()
	defer b.mu.RUnlock()
	return len(b.tabelas)
}

// LeiturasEvitadas conta consultas a tabelas poupadas pelo filtro de Bloom.
func (b *Banco) LeiturasEvitadas() uint64 { return b.evitadas.Load() }

// Fechar descarrega a memtable e libera os arquivos.
func (b *Banco) Fechar() error {
	b.mu.Lock()
	defer b.mu.Unlock()
	if b.fechado {
		return nil
	}
	err := b.descarregar()
	b.fechado = true
	b.fecharTabelas()
	return err
}
