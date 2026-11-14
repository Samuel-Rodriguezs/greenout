// Pacote segtree implementa uma árvore de segmentos de soma com propagação
// preguiçosa (lazy): soma em intervalo e consulta de soma em intervalo.
package segtree

// Arvore de soma com atualização de intervalo.
type Arvore struct {
	n    int
	soma []int
	lazy []int
}

// Nova constrói a árvore a partir dos valores iniciais.
func Nova(valores []int) *Arvore {
	t := &Arvore{n: len(valores)}
	if t.n == 0 {
		return t
	}
	t.soma = make([]int, 4*t.n)
	t.lazy = make([]int, 4*t.n)
	t.constroi(1, 0, t.n-1, valores)
	return t
}

func (t *Arvore) constroi(no, l, r int, v []int) {
	if l == r {
		t.soma[no] = v[l]
		return
	}
	m := (l + r) / 2
	t.constroi(2*no, l, m, v)
	t.constroi(2*no+1, m+1, r, v)
	t.soma[no] = t.soma[2*no] + t.soma[2*no+1]
}

func (t *Arvore) aplica(no, l, r, delta int) {
	t.soma[no] += delta * (r - l + 1)
	t.lazy[no] += delta
}

func (t *Arvore) empurra(no, l, r int) {
	if t.lazy[no] == 0 {
		return
	}
	m := (l + r) / 2
	t.aplica(2*no, l, m, t.lazy[no])
	t.aplica(2*no+1, m+1, r, t.lazy[no])
	t.lazy[no] = 0
}

// Somar adiciona delta a todas as posições de [l, r].
func (t *Arvore) Somar(l, r, delta int) {
	if t.n == 0 || l > r {
		return
	}
	t.soma1(1, 0, t.n-1, max(l, 0), min(r, t.n-1), delta)
}

func (t *Arvore) soma1(no, l, r, ql, qr, delta int) {
	if qr < l || r < ql {
		return
	}
	if ql <= l && r <= qr {
		t.aplica(no, l, r, delta)
		return
	}
	t.empurra(no, l, r)
	m := (l + r) / 2
	t.soma1(2*no, l, m, ql, qr, delta)
	t.soma1(2*no+1, m+1, r, ql, qr, delta)
	t.soma[no] = t.soma[2*no] + t.soma[2*no+1]
}

// Consultar devolve a soma de [l, r].
func (t *Arvore) Consultar(l, r int) int {
	if t.n == 0 || l > r {
		return 0
	}
	return t.consulta(1, 0, t.n-1, max(l, 0), min(r, t.n-1))
}

func (t *Arvore) consulta(no, l, r, ql, qr int) int {
	if qr < l || r < ql {
		return 0
	}
	if ql <= l && r <= qr {
		return t.soma[no]
	}
	t.empurra(no, l, r)
	m := (l + r) / 2
	return t.consulta(2*no, l, m, ql, qr) + t.consulta(2*no+1, m+1, r, ql, qr)
}
