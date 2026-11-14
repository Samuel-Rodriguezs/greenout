// Pacote heap implementa um heap binário genérico com comparador customizado.
package heap

// Heap mantém no topo o elemento que "vem antes" segundo o comparador.
type Heap[T any] struct {
	itens []T
	antes func(a, b T) bool
}

// Novo cria um heap. antes(a, b) deve retornar true se a deve sair antes de b
// (por exemplo, a < b para um min-heap).
func Novo[T any](antes func(a, b T) bool) *Heap[T] {
	return &Heap[T]{antes: antes}
}

// Tamanho devolve a quantidade de elementos.
func (h *Heap[T]) Tamanho() int { return len(h.itens) }

// Inserir adiciona um elemento em O(log n).
func (h *Heap[T]) Inserir(v T) {
	h.itens = append(h.itens, v)
	h.subir(len(h.itens) - 1)
}

// Topo espia o primeiro elemento sem remover.
func (h *Heap[T]) Topo() (v T, ok bool) {
	if len(h.itens) == 0 {
		return v, false
	}
	return h.itens[0], true
}

// Extrair remove e devolve o primeiro elemento em O(log n).
func (h *Heap[T]) Extrair() (v T, ok bool) {
	n := len(h.itens)
	if n == 0 {
		return v, false
	}
	v = h.itens[0]
	h.itens[0] = h.itens[n-1]
	var zero T
	h.itens[n-1] = zero
	h.itens = h.itens[:n-1]
	if n > 1 {
		h.descer(0)
	}
	return v, true
}

func (h *Heap[T]) subir(i int) {
	for i > 0 {
		pai := (i - 1) / 2
		if !h.antes(h.itens[i], h.itens[pai]) {
			return
		}
		h.itens[i], h.itens[pai] = h.itens[pai], h.itens[i]
		i = pai
	}
}

func (h *Heap[T]) descer(i int) {
	n := len(h.itens)
	for {
		menor := i
		if e := 2*i + 1; e < n && h.antes(h.itens[e], h.itens[menor]) {
			menor = e
		}
		if d := 2*i + 2; d < n && h.antes(h.itens[d], h.itens[menor]) {
			menor = d
		}
		if menor == i {
			return
		}
		h.itens[i], h.itens[menor] = h.itens[menor], h.itens[i]
		i = menor
	}
}
