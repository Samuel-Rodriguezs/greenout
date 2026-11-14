// Pacote anel implementa um buffer circular (ring buffer) genérico de capacidade fixa.
package anel

// Anel guarda até cap elementos; ao encher, escrever sobrescreve o mais antigo.
type Anel[T any] struct {
	buf []T
	ini int
	tam int
}

// Novo cria um anel com a capacidade informada. Capacidade < 1 vira 1.
func Novo[T any](capacidade int) *Anel[T] {
	return &Anel[T]{buf: make([]T, max(1, capacidade))}
}

// Escrever adiciona v; devolve true se sobrescreveu um elemento antigo.
func (a *Anel[T]) Escrever(v T) (sobrescreveu bool) {
	if a.tam == len(a.buf) {
		a.buf[a.ini] = v
		a.ini = (a.ini + 1) % len(a.buf)
		return true
	}
	a.buf[(a.ini+a.tam)%len(a.buf)] = v
	a.tam++
	return false
}

// Ler remove e devolve o elemento mais antigo.
func (a *Anel[T]) Ler() (v T, ok bool) {
	if a.tam == 0 {
		return v, false
	}
	v = a.buf[a.ini]
	var zero T
	a.buf[a.ini] = zero
	a.ini = (a.ini + 1) % len(a.buf)
	a.tam--
	return v, true
}

// Tamanho devolve a quantidade de elementos armazenados.
func (a *Anel[T]) Tamanho() int { return a.tam }

// Capacidade devolve a capacidade fixa.
func (a *Anel[T]) Capacidade() int { return len(a.buf) }

// Cheio informa se o anel está cheio.
func (a *Anel[T]) Cheio() bool { return a.tam == len(a.buf) }

// Itens devolve uma cópia dos elementos, do mais antigo ao mais novo.
func (a *Anel[T]) Itens() []T {
	r := make([]T, a.tam)
	for i := range r {
		r[i] = a.buf[(a.ini+i)%len(a.buf)]
	}
	return r
}
