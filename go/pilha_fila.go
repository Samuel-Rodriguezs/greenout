package lab

import "errors"

// ErrEstruturaVazia é devolvido ao remover de uma pilha ou fila vazia.
var ErrEstruturaVazia = errors.New("estrutura vazia")

// PilhaGen é uma pilha (LIFO) genérica.
type PilhaGen[T any] struct {
	itens []T
}

// Empilhar insere v no topo.
func (p *PilhaGen[T]) Empilhar(v T) { p.itens = append(p.itens, v) }

// Desempilhar remove e devolve o topo.
func (p *PilhaGen[T]) Desempilhar() (T, error) {
	var zero T
	if len(p.itens) == 0 {
		return zero, ErrEstruturaVazia
	}
	ultimo := len(p.itens) - 1
	v := p.itens[ultimo]
	p.itens[ultimo] = zero
	p.itens = p.itens[:ultimo]
	return v, nil
}

// Topo devolve o topo sem remover.
func (p *PilhaGen[T]) Topo() (T, error) {
	var zero T
	if len(p.itens) == 0 {
		return zero, ErrEstruturaVazia
	}
	return p.itens[len(p.itens)-1], nil
}

// Tamanho devolve a quantidade de itens.
func (p *PilhaGen[T]) Tamanho() int { return len(p.itens) }

// FilaGen é uma fila (FIFO) genérica.
type FilaGen[T any] struct {
	itens []T
}

// Enfileirar insere v no fim.
func (f *FilaGen[T]) Enfileirar(v T) { f.itens = append(f.itens, v) }

// Desenfileirar remove e devolve o primeiro item.
func (f *FilaGen[T]) Desenfileirar() (T, error) {
	var zero T
	if len(f.itens) == 0 {
		return zero, ErrEstruturaVazia
	}
	v := f.itens[0]
	f.itens[0] = zero
	f.itens = f.itens[1:]
	return v, nil
}

// Frente devolve o primeiro item sem remover.
func (f *FilaGen[T]) Frente() (T, error) {
	var zero T
	if len(f.itens) == 0 {
		return zero, ErrEstruturaVazia
	}
	return f.itens[0], nil
}

// Tamanho devolve a quantidade de itens.
func (f *FilaGen[T]) Tamanho() int { return len(f.itens) }
