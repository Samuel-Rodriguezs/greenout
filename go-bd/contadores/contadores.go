// Pacote contadores oferece contadores atômicos e um conjunto de contadores
// nomeados, como os usados para estatísticas internas de um banco
// (leituras, escritas, acertos de cache, ...).
package contadores

import (
	"sort"
	"sync"
	"sync/atomic"
)

// Contador é um inteiro de 64 bits seguro para uso concorrente.
type Contador struct {
	v atomic.Int64
}

// Incrementar soma n e devolve o novo valor.
func (c *Contador) Incrementar(n int64) int64 { return c.v.Add(n) }

// Decrementar subtrai n e devolve o novo valor.
func (c *Contador) Decrementar(n int64) int64 { return c.v.Add(-n) }

// Valor lê o valor atual.
func (c *Contador) Valor() int64 { return c.v.Load() }

// Zerar volta a zero e devolve o valor anterior.
func (c *Contador) Zerar() int64 { return c.v.Swap(0) }

// Maximo eleva o contador a n se n for maior; devolve o valor resultante.
func (c *Contador) Maximo(n int64) int64 {
	for {
		atual := c.v.Load()
		if n <= atual {
			return atual
		}
		if c.v.CompareAndSwap(atual, n) {
			return n
		}
	}
}

// Conjunto agrupa contadores identificados por nome; os contadores são
// criados no primeiro uso.
type Conjunto struct {
	mu sync.RWMutex
	m  map[string]*Contador
}

// NovoConjunto cria um conjunto vazio.
func NovoConjunto() *Conjunto { return &Conjunto{m: map[string]*Contador{}} }

func (s *Conjunto) contador(nome string) *Contador {
	s.mu.RLock()
	c := s.m[nome]
	s.mu.RUnlock()
	if c != nil {
		return c
	}
	s.mu.Lock()
	defer s.mu.Unlock()
	if c = s.m[nome]; c == nil {
		c = &Contador{}
		s.m[nome] = c
	}
	return c
}

// Incrementar soma n ao contador nome e devolve o novo valor.
func (s *Conjunto) Incrementar(nome string, n int64) int64 {
	return s.contador(nome).Incrementar(n)
}

// Valor lê o contador; contadores inexistentes valem 0 e não são criados.
func (s *Conjunto) Valor(nome string) int64 {
	s.mu.RLock()
	c := s.m[nome]
	s.mu.RUnlock()
	if c == nil {
		return 0
	}
	return c.Valor()
}

// Remover apaga o contador e devolve seu último valor.
func (s *Conjunto) Remover(nome string) (int64, bool) {
	s.mu.Lock()
	c, ok := s.m[nome]
	delete(s.m, nome)
	s.mu.Unlock()
	if !ok {
		return 0, false
	}
	return c.Valor(), true
}

// Nomes lista os contadores existentes em ordem alfabética.
func (s *Conjunto) Nomes() []string {
	s.mu.RLock()
	defer s.mu.RUnlock()
	ns := make([]string, 0, len(s.m))
	for n := range s.m {
		ns = append(ns, n)
	}
	sort.Strings(ns)
	return ns
}

// Instantaneo devolve uma cópia dos valores de todos os contadores.
func (s *Conjunto) Instantaneo() map[string]int64 {
	s.mu.RLock()
	defer s.mu.RUnlock()
	out := make(map[string]int64, len(s.m))
	for n, c := range s.m {
		out[n] = c.Valor()
	}
	return out
}
