// Pacote pagina implementa uma página "slotted" de tamanho fixo, como a de
// bancos relacionais: o diretório de slots cresce a partir do início e os
// registros crescem a partir do fim. A página serializa para bytes com
// checksum CRC32 e valida o conteúdo ao ser carregada.
//
// Layout (little endian):
//
//	[0:4]  crc32 dos bytes [4:Tamanho]
//	[4:6]  número de slots
//	[6:8]  início da área de dados (fim livre)
//	[8:..] slots de 4 bytes: offset uint16, tamanho uint16 (offset 0 = slot livre)
package pagina

import (
	"encoding/binary"
	"errors"
	"hash/crc32"
	"sort"
)

const (
	// Tamanho é o tamanho fixo de uma página em bytes.
	Tamanho   = 4096
	cabecalho = 8
	tamSlot   = 4
	// MaxRegistro é o maior registro que cabe numa página vazia.
	MaxRegistro = Tamanho - cabecalho - tamSlot
)

var (
	// ErrSemEspaco indica que o registro não cabe na página.
	ErrSemEspaco = errors.New("pagina: sem espaço")
	// ErrSlotInvalido indica um número de slot fora do diretório.
	ErrSlotInvalido = errors.New("pagina: slot inválido")
	// ErrRemovido indica que o slot foi removido.
	ErrRemovido = errors.New("pagina: slot removido")
	// ErrChecksum indica que o CRC não confere.
	ErrChecksum = errors.New("pagina: checksum inválido")
	// ErrCorrompida indica estrutura interna inconsistente.
	ErrCorrompida = errors.New("pagina: estrutura corrompida")
)

var tabela = crc32.MakeTable(crc32.IEEE)

// Pagina é uma página slotted em memória.
type Pagina struct {
	b [Tamanho]byte
}

// Nova cria uma página vazia.
func Nova() *Pagina {
	p := &Pagina{}
	p.defFim(Tamanho)
	return p
}

func (p *Pagina) numSlots() int     { return int(binary.LittleEndian.Uint16(p.b[4:6])) }
func (p *Pagina) fim() int          { return int(binary.LittleEndian.Uint16(p.b[6:8])) }
func (p *Pagina) defNum(n int)      { binary.LittleEndian.PutUint16(p.b[4:6], uint16(n)) }
func (p *Pagina) defFim(f int)      { binary.LittleEndian.PutUint16(p.b[6:8], uint16(f)) }
func (p *Pagina) posSlot(i int) int { return cabecalho + i*tamSlot }

func (p *Pagina) slot(i int) (off, tam int) {
	s := p.posSlot(i)
	return int(binary.LittleEndian.Uint16(p.b[s:])), int(binary.LittleEndian.Uint16(p.b[s+2:]))
}

func (p *Pagina) defSlot(i, off, tam int) {
	s := p.posSlot(i)
	binary.LittleEndian.PutUint16(p.b[s:], uint16(off))
	binary.LittleEndian.PutUint16(p.b[s+2:], uint16(tam))
}

// NumSlots devolve o tamanho do diretório (inclui slots removidos).
func (p *Pagina) NumSlots() int { return p.numSlots() }

// usado soma os bytes dos registros vivos.
func (p *Pagina) usado() int {
	total := 0
	for i := 0; i < p.numSlots(); i++ {
		if off, tam := p.slot(i); off != 0 {
			total += tam
		}
	}
	return total
}

// EspacoLivre devolve os bytes aproveitáveis (após compactação) para dados e slots.
func (p *Pagina) EspacoLivre() int {
	return Tamanho - cabecalho - p.numSlots()*tamSlot - p.usado()
}

func (p *Pagina) contiguo() int {
	return p.fim() - (cabecalho + p.numSlots()*tamSlot)
}

func (p *Pagina) slotLivre() int {
	for i := 0; i < p.numSlots(); i++ {
		if off, _ := p.slot(i); off == 0 {
			return i
		}
	}
	return -1
}

// Inserir guarda o registro e devolve o número do slot. Slots removidos são reaproveitados.
func (p *Pagina) Inserir(dados []byte) (int, error) {
	idx := p.slotLivre()
	precisa := len(dados)
	if idx < 0 {
		precisa += tamSlot
	}
	if len(dados) > MaxRegistro || precisa > p.EspacoLivre() {
		return 0, ErrSemEspaco
	}
	if precisa > p.contiguo() {
		p.Compactar()
	}
	if idx < 0 {
		idx = p.numSlots()
		p.defNum(idx + 1)
		p.defSlot(idx, 0, 0)
	}
	p.colocar(idx, dados)
	return idx, nil
}

// colocar grava os dados no fim da área livre e aponta o slot para eles.
func (p *Pagina) colocar(idx int, dados []byte) {
	f := p.fim() - len(dados)
	copy(p.b[f:], dados)
	p.defFim(f)
	p.defSlot(idx, f, len(dados))
}

func (p *Pagina) validarSlot(i int) (off, tam int, err error) {
	if i < 0 || i >= p.numSlots() {
		return 0, 0, ErrSlotInvalido
	}
	off, tam = p.slot(i)
	if off == 0 {
		return 0, 0, ErrRemovido
	}
	return off, tam, nil
}

// Ler devolve uma cópia do registro do slot.
func (p *Pagina) Ler(i int) ([]byte, error) {
	off, tam, err := p.validarSlot(i)
	if err != nil {
		return nil, err
	}
	return append([]byte(nil), p.b[off:off+tam]...), nil
}

// Remover marca o slot como livre; o espaço volta após Compactar ou numa inserção.
func (p *Pagina) Remover(i int) error {
	if _, _, err := p.validarSlot(i); err != nil {
		return err
	}
	p.defSlot(i, 0, 0)
	return nil
}

// Atualizar troca o conteúdo do slot mantendo seu número. Se não couber, a
// página permanece intacta e ErrSemEspaco é devolvido.
func (p *Pagina) Atualizar(i int, dados []byte) error {
	off, tam, err := p.validarSlot(i)
	if err != nil {
		return err
	}
	if len(dados) <= tam {
		copy(p.b[off:], dados)
		p.defSlot(i, off, len(dados))
		return nil
	}
	if len(dados) > p.EspacoLivre()+tam {
		return ErrSemEspaco
	}
	p.defSlot(i, 0, 0)
	if len(dados) > p.contiguo() {
		p.Compactar()
	}
	p.colocar(i, dados)
	return nil
}

// Compactar empurra todos os registros vivos para o fim da página.
func (p *Pagina) Compactar() {
	type reg struct {
		slot int
		d    []byte
	}
	var regs []reg
	for i := 0; i < p.numSlots(); i++ {
		if off, tam := p.slot(i); off != 0 {
			regs = append(regs, reg{i, append([]byte(nil), p.b[off:off+tam]...)})
		}
	}
	sort.Slice(regs, func(a, b int) bool { return regs[a].slot < regs[b].slot })
	fim := Tamanho
	for _, r := range regs {
		fim -= len(r.d)
		copy(p.b[fim:], r.d)
		p.defSlot(r.slot, fim, len(r.d))
	}
	// zera a área livre para que as páginas serializadas sejam determinísticas
	ini := cabecalho + p.numSlots()*tamSlot
	for j := ini; j < fim; j++ {
		p.b[j] = 0
	}
	p.defFim(fim)
}

// Bytes serializa a página (com o CRC atualizado).
func (p *Pagina) Bytes() []byte {
	binary.LittleEndian.PutUint32(p.b[0:4], crc32.Checksum(p.b[4:], tabela))
	return append([]byte(nil), p.b[:]...)
}

// Carregar reconstrói uma página a partir de bytes serializados, validando
// tamanho, checksum e a coerência do diretório de slots.
func Carregar(dados []byte) (*Pagina, error) {
	if len(dados) != Tamanho {
		return nil, ErrCorrompida
	}
	p := &Pagina{}
	copy(p.b[:], dados)
	if binary.LittleEndian.Uint32(p.b[0:4]) != crc32.Checksum(p.b[4:], tabela) {
		return nil, ErrChecksum
	}
	n, fim := p.numSlots(), p.fim()
	if fim > Tamanho || cabecalho+n*tamSlot > fim {
		return nil, ErrCorrompida
	}
	for i := 0; i < n; i++ {
		off, tam := p.slot(i)
		if off == 0 {
			continue
		}
		if off < fim || off+tam > Tamanho {
			return nil, ErrCorrompida
		}
	}
	return p, nil
}
