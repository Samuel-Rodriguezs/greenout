// Pacote heapfile implementa um heap file: registros de tamanho variável
// guardados em páginas slotted (pacote pagina) num único arquivo e
// endereçados por RID (página + slot).
package heapfile

import (
	"errors"
	"fmt"
	"os"
	"sync"

	"greenout/bd/pagina"
)

var (
	// ErrGrande indica registro maior que uma página vazia comporta.
	ErrGrande = errors.New("heapfile: registro grande demais")
	// ErrRIDInvalido indica RID fora do arquivo.
	ErrRIDInvalido = errors.New("heapfile: RID inválido")
	// ErrCorrompido indica arquivo com tamanho ou páginas inválidos.
	ErrCorrompido = errors.New("heapfile: arquivo corrompido")
	// ErrFechado indica uso após Fechar.
	ErrFechado = errors.New("heapfile: arquivo fechado")
)

// RID identifica um registro: número da página e do slot.
type RID struct {
	Pagina uint32
	Slot   uint16
}

func (r RID) String() string { return fmt.Sprintf("(%d,%d)", r.Pagina, r.Slot) }

// Arquivo é um heap file.
type Arquivo struct {
	mu    sync.Mutex
	f     *os.File
	livre []int // espaço livre conhecido de cada página
}

// Abrir abre ou cria o arquivo, validando todas as páginas existentes.
func Abrir(caminho string) (*Arquivo, error) {
	f, err := os.OpenFile(caminho, os.O_CREATE|os.O_RDWR, 0o644)
	if err != nil {
		return nil, err
	}
	a := &Arquivo{f: f}
	info, err := f.Stat()
	if err != nil {
		f.Close()
		return nil, err
	}
	if info.Size()%pagina.Tamanho != 0 {
		f.Close()
		return nil, fmt.Errorf("%w: tamanho %d não é múltiplo da página", ErrCorrompido, info.Size())
	}
	n := int(info.Size() / pagina.Tamanho)
	for i := 0; i < n; i++ {
		p, err := a.ler(uint32(i))
		if err != nil {
			f.Close()
			return nil, fmt.Errorf("%w: página %d: %v", ErrCorrompido, i, err)
		}
		a.livre = append(a.livre, p.EspacoLivre())
	}
	return a, nil
}

func (a *Arquivo) ler(n uint32) (*pagina.Pagina, error) {
	buf := make([]byte, pagina.Tamanho)
	if _, err := a.f.ReadAt(buf, int64(n)*pagina.Tamanho); err != nil {
		return nil, err
	}
	return pagina.Carregar(buf)
}

func (a *Arquivo) gravar(n uint32, p *pagina.Pagina) error {
	_, err := a.f.WriteAt(p.Bytes(), int64(n)*pagina.Tamanho)
	return err
}

// NumPaginas devolve quantas páginas o arquivo possui.
func (a *Arquivo) NumPaginas() int {
	a.mu.Lock()
	defer a.mu.Unlock()
	return len(a.livre)
}

// Inserir grava o registro na primeira página com espaço e devolve o RID.
func (a *Arquivo) Inserir(dados []byte) (RID, error) {
	a.mu.Lock()
	defer a.mu.Unlock()
	if a.f == nil {
		return RID{}, ErrFechado
	}
	return a.inserir(dados)
}

func (a *Arquivo) inserir(dados []byte) (RID, error) {
	if len(dados) > pagina.MaxRegistro {
		return RID{}, ErrGrande
	}
	precisa := len(dados) + 4
	alvo := -1
	for i, l := range a.livre {
		if l >= precisa {
			alvo = i
			break
		}
	}
	var p *pagina.Pagina
	novaPagina := alvo < 0
	if novaPagina {
		alvo = len(a.livre)
		p = pagina.Nova()
	} else {
		var err error
		if p, err = a.ler(uint32(alvo)); err != nil {
			return RID{}, err
		}
	}
	slot, err := p.Inserir(dados)
	if err != nil {
		return RID{}, err
	}
	if err := a.gravar(uint32(alvo), p); err != nil {
		return RID{}, err
	}
	if novaPagina {
		a.livre = append(a.livre, 0)
	}
	a.livre[alvo] = p.EspacoLivre()
	return RID{uint32(alvo), uint16(slot)}, nil
}

func (a *Arquivo) pagina(r RID) (*pagina.Pagina, error) {
	if int(r.Pagina) >= len(a.livre) {
		return nil, ErrRIDInvalido
	}
	return a.ler(r.Pagina)
}

// Ler devolve o registro apontado pelo RID.
func (a *Arquivo) Ler(r RID) ([]byte, error) {
	a.mu.Lock()
	defer a.mu.Unlock()
	if a.f == nil {
		return nil, ErrFechado
	}
	p, err := a.pagina(r)
	if err != nil {
		return nil, err
	}
	return p.Ler(int(r.Slot))
}

// Remover apaga o registro.
func (a *Arquivo) Remover(r RID) error {
	a.mu.Lock()
	defer a.mu.Unlock()
	if a.f == nil {
		return ErrFechado
	}
	p, err := a.pagina(r)
	if err != nil {
		return err
	}
	if err := p.Remover(int(r.Slot)); err != nil {
		return err
	}
	if err := a.gravar(r.Pagina, p); err != nil {
		return err
	}
	a.livre[r.Pagina] = p.EspacoLivre()
	return nil
}

// Atualizar troca o conteúdo. Se não couber na página original, o registro
// é movido e o novo RID é devolvido (o antigo deixa de valer).
func (a *Arquivo) Atualizar(r RID, dados []byte) (RID, error) {
	a.mu.Lock()
	defer a.mu.Unlock()
	if a.f == nil {
		return RID{}, ErrFechado
	}
	if len(dados) > pagina.MaxRegistro {
		return RID{}, ErrGrande
	}
	p, err := a.pagina(r)
	if err != nil {
		return RID{}, err
	}
	err = p.Atualizar(int(r.Slot), dados)
	if err == nil {
		if err := a.gravar(r.Pagina, p); err != nil {
			return RID{}, err
		}
		a.livre[r.Pagina] = p.EspacoLivre()
		return r, nil
	}
	if !errors.Is(err, pagina.ErrSemEspaco) {
		return RID{}, err
	}
	novo, err := a.inserir(dados)
	if err != nil {
		return RID{}, err
	}
	// reler: a inserção pode ter caído na mesma página
	p, err = a.pagina(r)
	if err != nil {
		return RID{}, err
	}
	if err := p.Remover(int(r.Slot)); err != nil {
		return RID{}, err
	}
	if err := a.gravar(r.Pagina, p); err != nil {
		return RID{}, err
	}
	a.livre[r.Pagina] = p.EspacoLivre()
	return novo, nil
}

// Varrer visita todos os registros vivos em ordem de RID; para se fn devolver false.
func (a *Arquivo) Varrer(fn func(RID, []byte) bool) error {
	a.mu.Lock()
	defer a.mu.Unlock()
	if a.f == nil {
		return ErrFechado
	}
	for n := range a.livre {
		p, err := a.ler(uint32(n))
		if err != nil {
			return err
		}
		for s := 0; s < p.NumSlots(); s++ {
			d, err := p.Ler(s)
			if errors.Is(err, pagina.ErrRemovido) {
				continue
			}
			if err != nil {
				return err
			}
			if !fn(RID{uint32(n), uint16(s)}, d) {
				return nil
			}
		}
	}
	return nil
}

// Sincronizar força os dados para o disco.
func (a *Arquivo) Sincronizar() error {
	a.mu.Lock()
	defer a.mu.Unlock()
	if a.f == nil {
		return ErrFechado
	}
	return a.f.Sync()
}

// Fechar fecha o arquivo.
func (a *Arquivo) Fechar() error {
	a.mu.Lock()
	defer a.mu.Unlock()
	if a.f == nil {
		return nil
	}
	err := a.f.Close()
	a.f = nil
	return err
}
