package lab

import "errors"

// ErrListaIndiceInvalido indica índice fora dos limites da lista.
var ErrListaIndiceInvalido = errors.New("lista: índice inválido")

type noLista[T any] struct {
	valor   T
	proximo *noLista[T]
}

// ListaEncadeada é uma lista simplesmente encadeada genérica.
type ListaEncadeada[T any] struct {
	cabeca *noLista[T]
	cauda  *noLista[T]
	n      int
}

// Tamanho devolve o número de elementos.
func (l *ListaEncadeada[T]) Tamanho() int { return l.n }

// Adicionar insere v no fim.
func (l *ListaEncadeada[T]) Adicionar(v T) {
	no := &noLista[T]{valor: v}
	if l.cauda == nil {
		l.cabeca, l.cauda = no, no
	} else {
		l.cauda.proximo = no
		l.cauda = no
	}
	l.n++
}

// AdicionarInicio insere v no começo.
func (l *ListaEncadeada[T]) AdicionarInicio(v T) {
	no := &noLista[T]{valor: v, proximo: l.cabeca}
	l.cabeca = no
	if l.cauda == nil {
		l.cauda = no
	}
	l.n++
}

// Obter devolve o elemento no índice i.
func (l *ListaEncadeada[T]) Obter(i int) (T, error) {
	var zero T
	if i < 0 || i >= l.n {
		return zero, ErrListaIndiceInvalido
	}
	no := l.cabeca
	for ; i > 0; i-- {
		no = no.proximo
	}
	return no.valor, nil
}

// Remover retira o elemento do índice i e o devolve.
func (l *ListaEncadeada[T]) Remover(i int) (T, error) {
	var zero T
	if i < 0 || i >= l.n {
		return zero, ErrListaIndiceInvalido
	}
	var anterior *noLista[T]
	no := l.cabeca
	for ; i > 0; i-- {
		anterior, no = no, no.proximo
	}
	if anterior == nil {
		l.cabeca = no.proximo
	} else {
		anterior.proximo = no.proximo
	}
	if no == l.cauda {
		l.cauda = anterior
	}
	l.n--
	return no.valor, nil
}

// Inverter inverte a lista in-place.
func (l *ListaEncadeada[T]) Inverter() {
	var anterior *noLista[T]
	no := l.cabeca
	l.cauda = l.cabeca
	for no != nil {
		prox := no.proximo
		no.proximo = anterior
		anterior, no = no, prox
	}
	l.cabeca = anterior
}

// ParaSlice devolve os elementos em ordem.
func (l *ListaEncadeada[T]) ParaSlice() []T {
	saida := make([]T, 0, l.n)
	for no := l.cabeca; no != nil; no = no.proximo {
		saida = append(saida, no.valor)
	}
	return saida
}
