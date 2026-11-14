// Pacote arvore implementa uma árvore binária de busca genérica.
package arvore

type no[T any] struct {
	valor    T
	esq, dir *no[T]
}

// Arvore é uma BST (sem balanceamento) ordenada por um comparador.
type Arvore[T any] struct {
	raiz *no[T]
	cmp  func(a, b T) int
	tam  int
}

// Nova cria uma árvore. cmp deve retornar <0, 0 ou >0 como strings.Compare.
func Nova[T any](cmp func(a, b T) int) *Arvore[T] {
	return &Arvore[T]{cmp: cmp}
}

// Tamanho devolve a quantidade de elementos.
func (a *Arvore[T]) Tamanho() int { return a.tam }

// Inserir adiciona v; retorna false se um elemento igual já existia (e o mantém).
func (a *Arvore[T]) Inserir(v T) bool {
	p := &a.raiz
	for *p != nil {
		switch c := a.cmp(v, (*p).valor); {
		case c < 0:
			p = &(*p).esq
		case c > 0:
			p = &(*p).dir
		default:
			return false
		}
	}
	*p = &no[T]{valor: v}
	a.tam++
	return true
}

// Buscar procura um elemento igual a v.
func (a *Arvore[T]) Buscar(v T) (T, bool) {
	for n := a.raiz; n != nil; {
		switch c := a.cmp(v, n.valor); {
		case c < 0:
			n = n.esq
		case c > 0:
			n = n.dir
		default:
			return n.valor, true
		}
	}
	var zero T
	return zero, false
}

// Remover apaga o elemento igual a v e informa se ele existia.
func (a *Arvore[T]) Remover(v T) bool {
	p := &a.raiz
	for *p != nil {
		c := a.cmp(v, (*p).valor)
		if c == 0 {
			break
		}
		if c < 0 {
			p = &(*p).esq
		} else {
			p = &(*p).dir
		}
	}
	n := *p
	if n == nil {
		return false
	}
	switch {
	case n.esq == nil:
		*p = n.dir
	case n.dir == nil:
		*p = n.esq
	default:
		// substitui pelo sucessor (menor da subárvore direita)
		sp := &n.dir
		for (*sp).esq != nil {
			sp = &(*sp).esq
		}
		suc := *sp
		*sp = suc.dir
		suc.esq, suc.dir = n.esq, n.dir
		*p = suc
	}
	a.tam--
	return true
}

// EmOrdem devolve os elementos em ordem crescente.
func (a *Arvore[T]) EmOrdem() []T {
	r := make([]T, 0, a.tam)
	var visita func(*no[T])
	visita = func(n *no[T]) {
		if n == nil {
			return
		}
		visita(n.esq)
		r = append(r, n.valor)
		visita(n.dir)
	}
	visita(a.raiz)
	return r
}

// Minimo devolve o menor elemento.
func (a *Arvore[T]) Minimo() (v T, ok bool) {
	if a.raiz == nil {
		return v, false
	}
	n := a.raiz
	for n.esq != nil {
		n = n.esq
	}
	return n.valor, true
}

// Maximo devolve o maior elemento.
func (a *Arvore[T]) Maximo() (v T, ok bool) {
	if a.raiz == nil {
		return v, false
	}
	n := a.raiz
	for n.dir != nil {
		n = n.dir
	}
	return n.valor, true
}

// Altura devolve a altura da árvore (vazia = 0, um nó = 1).
func (a *Arvore[T]) Altura() int {
	var h func(*no[T]) int
	h = func(n *no[T]) int {
		if n == nil {
			return 0
		}
		return 1 + max(h(n.esq), h(n.dir))
	}
	return h(a.raiz)
}
