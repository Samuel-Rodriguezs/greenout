package lab

import "cmp"

type noArvore[T cmp.Ordered] struct {
	valor    T
	esq, dir *noArvore[T]
}

// ArvoreBusca é uma árvore binária de busca (sem duplicados).
type ArvoreBusca[T cmp.Ordered] struct {
	raiz *noArvore[T]
	n    int
}

// Tamanho devolve o número de elementos.
func (a *ArvoreBusca[T]) Tamanho() int { return a.n }

// Inserir adiciona v; devolve false se já existia.
func (a *ArvoreBusca[T]) Inserir(v T) bool {
	p := &a.raiz
	for *p != nil {
		switch c := cmp.Compare(v, (*p).valor); {
		case c == 0:
			return false
		case c < 0:
			p = &(*p).esq
		default:
			p = &(*p).dir
		}
	}
	*p = &noArvore[T]{valor: v}
	a.n++
	return true
}

// Contem informa se v está na árvore.
func (a *ArvoreBusca[T]) Contem(v T) bool {
	no := a.raiz
	for no != nil {
		switch c := cmp.Compare(v, no.valor); {
		case c == 0:
			return true
		case c < 0:
			no = no.esq
		default:
			no = no.dir
		}
	}
	return false
}

// Remover exclui v; devolve false se não existia.
func (a *ArvoreBusca[T]) Remover(v T) bool {
	p := &a.raiz
	for *p != nil && (*p).valor != v {
		if v < (*p).valor {
			p = &(*p).esq
		} else {
			p = &(*p).dir
		}
	}
	if *p == nil {
		return false
	}
	no := *p
	switch {
	case no.esq == nil:
		*p = no.dir
	case no.dir == nil:
		*p = no.esq
	default:
		// sucessor: menor nó da subárvore direita
		s := &no.dir
		for (*s).esq != nil {
			s = &(*s).esq
		}
		suc := *s
		*s = suc.dir
		suc.esq, suc.dir = no.esq, no.dir
		*p = suc
	}
	a.n--
	return true
}

// EmOrdem devolve os valores em ordem crescente.
func (a *ArvoreBusca[T]) EmOrdem() []T {
	saida := make([]T, 0, a.n)
	var visita func(*noArvore[T])
	visita = func(no *noArvore[T]) {
		if no == nil {
			return
		}
		visita(no.esq)
		saida = append(saida, no.valor)
		visita(no.dir)
	}
	visita(a.raiz)
	return saida
}

// Altura devolve a altura da árvore (vazia = 0).
func (a *ArvoreBusca[T]) Altura() int {
	var h func(*noArvore[T]) int
	h = func(no *noArvore[T]) int {
		if no == nil {
			return 0
		}
		return 1 + max(h(no.esq), h(no.dir))
	}
	return h(a.raiz)
}
