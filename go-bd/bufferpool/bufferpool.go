// Pacote bufferpool implementa um buffer pool com política LRU: páginas são
// fixadas (pin) enquanto em uso, e a menos recentemente usada entre as não
// fixadas é despejada, sendo gravada antes se estiver suja.
package bufferpool

import (
	"container/list"
	"errors"
	"io"
	"os"
	"sync"
)

var (
	// ErrPoolCheio indica que todas as páginas residentes estão fixadas.
	ErrPoolCheio = errors.New("bufferpool: todas as páginas estão fixadas")
	// ErrNaoFixada indica Liberar numa página sem pin.
	ErrNaoFixada = errors.New("bufferpool: página não está fixada")
	// ErrCapacidade indica capacidade inválida.
	ErrCapacidade = errors.New("bufferpool: capacidade deve ser >= 1")
)

// Disco é o armazenamento de páginas por trás do pool.
type Disco interface {
	LerPagina(id uint32, dst []byte) error
	EscreverPagina(id uint32, src []byte) error
}

// Quadro é uma página residente em memória.
type Quadro struct {
	ID    uint32
	Dados []byte
	pins  int
	sujo  bool
	elem  *list.Element
}

// Estatisticas resume o uso do pool.
type Estatisticas struct {
	Acertos, Faltas, Despejos, Gravacoes uint64
}

// Pool é o buffer pool.
type Pool struct {
	mu      sync.Mutex
	disco   Disco
	cap     int
	tam     int
	quadros map[uint32]*Quadro
	lru     *list.List // frente = mais recente
	est     Estatisticas
}

// Novo cria um pool com a capacidade (em páginas) e o tamanho de página dados.
func Novo(disco Disco, capacidade, tamPagina int) (*Pool, error) {
	if capacidade < 1 || tamPagina < 1 {
		return nil, ErrCapacidade
	}
	return &Pool{disco: disco, cap: capacidade, tam: tamPagina,
		quadros: map[uint32]*Quadro{}, lru: list.New()}, nil
}

// Buscar devolve a página fixada, lendo-a do disco se necessário. Cada
// Buscar deve ser pareado com um Liberar.
func (p *Pool) Buscar(id uint32) (*Quadro, error) {
	p.mu.Lock()
	defer p.mu.Unlock()
	if q, ok := p.quadros[id]; ok {
		p.est.Acertos++
		q.pins++
		p.lru.MoveToFront(q.elem)
		return q, nil
	}
	p.est.Faltas++
	if len(p.quadros) >= p.cap {
		if err := p.despejar(); err != nil {
			return nil, err
		}
	}
	q := &Quadro{ID: id, Dados: make([]byte, p.tam), pins: 1}
	if err := p.disco.LerPagina(id, q.Dados); err != nil {
		return nil, err
	}
	q.elem = p.lru.PushFront(q)
	p.quadros[id] = q
	return q, nil
}

// despejar remove a página não fixada menos recente. p.mu deve estar travado.
func (p *Pool) despejar() error {
	for e := p.lru.Back(); e != nil; e = e.Prev() {
		q := e.Value.(*Quadro)
		if q.pins > 0 {
			continue
		}
		if q.sujo {
			if err := p.disco.EscreverPagina(q.ID, q.Dados); err != nil {
				return err
			}
			p.est.Gravacoes++
			q.sujo = false
		}
		p.lru.Remove(e)
		delete(p.quadros, q.ID)
		p.est.Despejos++
		return nil
	}
	return ErrPoolCheio
}

// Liberar solta um pin; sujo marca a página como modificada.
func (p *Pool) Liberar(id uint32, sujo bool) error {
	p.mu.Lock()
	defer p.mu.Unlock()
	q, ok := p.quadros[id]
	if !ok || q.pins == 0 {
		return ErrNaoFixada
	}
	q.pins--
	if sujo {
		q.sujo = true
	}
	return nil
}

// Descarregar grava todas as páginas sujas sem despejá-las.
func (p *Pool) Descarregar() error {
	p.mu.Lock()
	defer p.mu.Unlock()
	for _, q := range p.quadros {
		if !q.sujo {
			continue
		}
		if err := p.disco.EscreverPagina(q.ID, q.Dados); err != nil {
			return err
		}
		p.est.Gravacoes++
		q.sujo = false
	}
	return nil
}

// Residentes devolve quantas páginas estão no pool.
func (p *Pool) Residentes() int {
	p.mu.Lock()
	defer p.mu.Unlock()
	return len(p.quadros)
}

// Estatisticas devolve uma cópia dos contadores.
func (p *Pool) Estatisticas() Estatisticas {
	p.mu.Lock()
	defer p.mu.Unlock()
	return p.est
}

// DiscoMemoria é um Disco em memória, útil em testes.
type DiscoMemoria struct {
	mu       sync.Mutex
	paginas  map[uint32][]byte
	Leituras int
	Escritas int
}

// NovoDiscoMemoria cria um disco vazio; páginas inexistentes leem como zeros.
func NovoDiscoMemoria() *DiscoMemoria { return &DiscoMemoria{paginas: map[uint32][]byte{}} }

// LerPagina implementa Disco.
func (d *DiscoMemoria) LerPagina(id uint32, dst []byte) error {
	d.mu.Lock()
	defer d.mu.Unlock()
	d.Leituras++
	clear(dst)
	copy(dst, d.paginas[id])
	return nil
}

// EscreverPagina implementa Disco.
func (d *DiscoMemoria) EscreverPagina(id uint32, src []byte) error {
	d.mu.Lock()
	defer d.mu.Unlock()
	d.Escritas++
	d.paginas[id] = append([]byte(nil), src...)
	return nil
}

// DiscoArquivo armazena páginas contíguas num arquivo.
type DiscoArquivo struct {
	f   *os.File
	tam int
}

// AbrirDiscoArquivo abre (ou cria) o arquivo de páginas.
func AbrirDiscoArquivo(caminho string, tamPagina int) (*DiscoArquivo, error) {
	f, err := os.OpenFile(caminho, os.O_CREATE|os.O_RDWR, 0o644)
	if err != nil {
		return nil, err
	}
	return &DiscoArquivo{f: f, tam: tamPagina}, nil
}

// LerPagina implementa Disco; páginas além do fim do arquivo leem como zeros.
func (d *DiscoArquivo) LerPagina(id uint32, dst []byte) error {
	n, err := d.f.ReadAt(dst, int64(id)*int64(d.tam))
	if err == io.EOF {
		clear(dst[n:])
		return nil
	}
	return err
}

// EscreverPagina implementa Disco.
func (d *DiscoArquivo) EscreverPagina(id uint32, src []byte) error {
	_, err := d.f.WriteAt(src, int64(id)*int64(d.tam))
	return err
}

// Fechar fecha o arquivo.
func (d *DiscoArquivo) Fechar() error { return d.f.Close() }
