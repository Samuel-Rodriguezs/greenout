// Pacote contador oferece contadores concorrentes com sharding para reduzir
// a contenção de mutex: um contador numérico e um contador por chave.
package contador

import (
	"hash/fnv"
	"sync"
	"sync/atomic"
)

const fragmentosPadrao = 16

type fragmento struct {
	mu sync.Mutex
	n  int64
	_  [40]byte // evita false sharing entre fragmentos vizinhos
}

// Contador soma valores de várias goroutines distribuindo-os entre fragmentos.
type Contador struct {
	frags []fragmento
	prox  atomic.Uint64
}

// Novo cria um contador com n fragmentos (n <= 0 usa o padrão de 16).
func Novo(n int) *Contador {
	if n <= 0 {
		n = fragmentosPadrao
	}
	return &Contador{frags: make([]fragmento, n)}
}

// Adicionar soma delta (pode ser negativo) em um fragmento escolhido em rodízio.
func (c *Contador) Adicionar(delta int64) {
	f := &c.frags[c.prox.Add(1)%uint64(len(c.frags))]
	f.mu.Lock()
	f.n += delta
	f.mu.Unlock()
}

// Incrementar soma 1.
func (c *Contador) Incrementar() { c.Adicionar(1) }

// Total devolve a soma de todos os fragmentos.
func (c *Contador) Total() int64 {
	var t int64
	for i := range c.frags {
		f := &c.frags[i]
		f.mu.Lock()
		t += f.n
		f.mu.Unlock()
	}
	return t
}

// Zerar reinicia todos os fragmentos.
func (c *Contador) Zerar() {
	for i := range c.frags {
		f := &c.frags[i]
		f.mu.Lock()
		f.n = 0
		f.mu.Unlock()
	}
}

type fragMapa struct {
	mu sync.Mutex
	m  map[string]int64
}

// PorChave conta ocorrências por chave, com um mutex por fragmento (hash da chave).
type PorChave struct {
	frags []fragMapa
}

// NovoPorChave cria um contador por chave com n fragmentos (n <= 0 usa 16).
func NovoPorChave(n int) *PorChave {
	if n <= 0 {
		n = fragmentosPadrao
	}
	p := &PorChave{frags: make([]fragMapa, n)}
	for i := range p.frags {
		p.frags[i].m = make(map[string]int64)
	}
	return p
}

func (p *PorChave) frag(chave string) *fragMapa {
	h := fnv.New32a()
	h.Write([]byte(chave))
	return &p.frags[h.Sum32()%uint32(len(p.frags))]
}

// Adicionar soma delta à chave e devolve o novo valor.
func (p *PorChave) Adicionar(chave string, delta int64) int64 {
	f := p.frag(chave)
	f.mu.Lock()
	defer f.mu.Unlock()
	f.m[chave] += delta
	return f.m[chave]
}

// Obter devolve o valor da chave (0 se inexistente).
func (p *PorChave) Obter(chave string) int64 {
	f := p.frag(chave)
	f.mu.Lock()
	defer f.mu.Unlock()
	return f.m[chave]
}

// Instantaneo devolve uma cópia de todos os valores.
func (p *PorChave) Instantaneo() map[string]int64 {
	r := make(map[string]int64)
	for i := range p.frags {
		f := &p.frags[i]
		f.mu.Lock()
		for k, v := range f.m {
			r[k] = v
		}
		f.mu.Unlock()
	}
	return r
}
