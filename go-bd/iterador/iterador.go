// Pacote iterador define iteradores ordenados sobre entradas chave-valor e
// combinadores: filtro por intervalo, limite, descarte de remoções e o
// merge iterator, que funde várias fontes ordenadas resolvendo chaves
// repetidas em favor da fonte mais recente.
package iterador

import "container/heap"

// Entrada é um par chave-valor; Apagado marca uma lápide (tombstone).
type Entrada struct {
	Chave   string
	Valor   []byte
	Apagado bool
}

// Iterador percorre entradas em ordem crescente de chave.
//
// Uso: for it.Proximo() { e := it.Entrada() ... }; depois conferir Erro().
type Iterador interface {
	Proximo() bool
	Entrada() Entrada
	Erro() error
}

// ---- fonte a partir de slice ----

type deSlice struct {
	es  []Entrada
	pos int
}

// DeSlice cria um iterador sobre um slice já ordenado por chave.
func DeSlice(es []Entrada) Iterador { return &deSlice{es: es, pos: -1} }

func (s *deSlice) Proximo() bool {
	if s.pos+1 >= len(s.es) {
		s.pos = len(s.es)
		return false
	}
	s.pos++
	return true
}
func (s *deSlice) Entrada() Entrada { return s.es[s.pos] }
func (s *deSlice) Erro() error      { return nil }

// ---- intervalo ----

type intervalo struct {
	it      Iterador
	de, ate string
	temAte  bool
	fim     bool
	atual   Entrada
}

// Intervalo restringe um iterador ordenado às chaves em [de, ate). Se
// ilimitado for true, ate é ignorado.
func Intervalo(it Iterador, de, ate string, ilimitado bool) Iterador {
	return &intervalo{it: it, de: de, ate: ate, temAte: !ilimitado}
}

func (r *intervalo) Proximo() bool {
	if r.fim {
		return false
	}
	for r.it.Proximo() {
		e := r.it.Entrada()
		if e.Chave < r.de {
			continue
		}
		if r.temAte && e.Chave >= r.ate {
			break
		}
		r.atual = e
		return true
	}
	r.fim = true
	return false
}
func (r *intervalo) Entrada() Entrada { return r.atual }
func (r *intervalo) Erro() error      { return r.it.Erro() }

// ---- limite ----

type limite struct {
	it    Iterador
	resto int
}

// Limitar entrega no máximo n entradas.
func Limitar(it Iterador, n int) Iterador { return &limite{it: it, resto: n} }

func (l *limite) Proximo() bool {
	if l.resto <= 0 {
		return false
	}
	if !l.it.Proximo() {
		l.resto = 0
		return false
	}
	l.resto--
	return true
}
func (l *limite) Entrada() Entrada { return l.it.Entrada() }
func (l *limite) Erro() error      { return l.it.Erro() }

// ---- sem apagados ----

type semApagados struct{ it Iterador }

// SemApagados descarta as lápides.
func SemApagados(it Iterador) Iterador { return &semApagados{it} }

func (s *semApagados) Proximo() bool {
	for s.it.Proximo() {
		if !s.it.Entrada().Apagado {
			return true
		}
	}
	return false
}
func (s *semApagados) Entrada() Entrada { return s.it.Entrada() }
func (s *semApagados) Erro() error      { return s.it.Erro() }

// ---- merge ----

type item struct {
	fonte int
	e     Entrada
}

type pilha []item

func (p pilha) Len() int { return len(p) }
func (p pilha) Less(i, j int) bool {
	if p[i].e.Chave != p[j].e.Chave {
		return p[i].e.Chave < p[j].e.Chave
	}
	return p[i].fonte < p[j].fonte
}
func (p pilha) Swap(i, j int) { p[i], p[j] = p[j], p[i] }
func (p *pilha) Push(x any)   { *p = append(*p, x.(item)) }
func (p *pilha) Pop() any {
	v := (*p)[len(*p)-1]
	*p = (*p)[:len(*p)-1]
	return v
}

type mescla struct {
	fontes   []Iterador
	h        pilha
	iniciado bool
	atual    Entrada
	err      error
}

// Mesclar funde fontes ordenadas. Quando a mesma chave aparece em várias
// fontes, vale a de menor índice (fontes[0] é a mais recente); as demais
// são descartadas. Lápides são preservadas: use SemApagados para removê-las.
func Mesclar(fontes ...Iterador) Iterador { return &mescla{fontes: fontes} }

func (m *mescla) avancar(i int) {
	if m.fontes[i].Proximo() {
		heap.Push(&m.h, item{i, m.fontes[i].Entrada()})
		return
	}
	if err := m.fontes[i].Erro(); err != nil && m.err == nil {
		m.err = err
	}
}

func (m *mescla) Proximo() bool {
	if m.err != nil {
		return false
	}
	if !m.iniciado {
		m.iniciado = true
		for i := range m.fontes {
			m.avancar(i)
		}
		if m.err != nil {
			return false
		}
	}
	if m.h.Len() == 0 {
		return false
	}
	topo := heap.Pop(&m.h).(item)
	m.atual = topo.e
	m.avancar(topo.fonte)
	for m.err == nil && m.h.Len() > 0 && m.h[0].e.Chave == m.atual.Chave {
		dup := heap.Pop(&m.h).(item)
		m.avancar(dup.fonte)
	}
	return m.err == nil
}
func (m *mescla) Entrada() Entrada { return m.atual }
func (m *mescla) Erro() error      { return m.err }

// Coletar esgota o iterador e devolve as entradas.
func Coletar(it Iterador) ([]Entrada, error) {
	var out []Entrada
	for it.Proximo() {
		out = append(out, it.Entrada())
	}
	return out, it.Erro()
}
