// Pacote pilhafila implementa Pilha (LIFO), Fila (FIFO) e Deque genéricos.
package pilhafila

// Pilha é uma estrutura LIFO.
type Pilha[T any] struct{ itens []T }

// Empilhar adiciona no topo.
func (p *Pilha[T]) Empilhar(v T) { p.itens = append(p.itens, v) }

// Desempilhar remove e devolve o topo; ok é false se vazia.
func (p *Pilha[T]) Desempilhar() (v T, ok bool) {
	if len(p.itens) == 0 {
		return v, false
	}
	n := len(p.itens) - 1
	v = p.itens[n]
	var zero T
	p.itens[n] = zero
	p.itens = p.itens[:n]
	return v, true
}

// Topo espia o topo sem remover.
func (p *Pilha[T]) Topo() (v T, ok bool) {
	if len(p.itens) == 0 {
		return v, false
	}
	return p.itens[len(p.itens)-1], true
}

// Tamanho devolve a quantidade de itens.
func (p *Pilha[T]) Tamanho() int { return len(p.itens) }

// Fila é uma estrutura FIFO com remoção amortizada O(1).
type Fila[T any] struct {
	itens []T
	ini   int
}

// Enfileirar adiciona no fim.
func (f *Fila[T]) Enfileirar(v T) { f.itens = append(f.itens, v) }

// Desenfileirar remove e devolve o primeiro; ok é false se vazia.
func (f *Fila[T]) Desenfileirar() (v T, ok bool) {
	if f.ini >= len(f.itens) {
		return v, false
	}
	v = f.itens[f.ini]
	var zero T
	f.itens[f.ini] = zero
	f.ini++
	if f.ini > 32 && f.ini*2 >= len(f.itens) { // compacta
		f.itens = append([]T(nil), f.itens[f.ini:]...)
		f.ini = 0
	}
	return v, true
}

// Frente espia o primeiro sem remover.
func (f *Fila[T]) Frente() (v T, ok bool) {
	if f.ini >= len(f.itens) {
		return v, false
	}
	return f.itens[f.ini], true
}

// Tamanho devolve a quantidade de itens.
func (f *Fila[T]) Tamanho() int { return len(f.itens) - f.ini }

// Deque é uma fila dupla baseada em buffer circular.
type Deque[T any] struct {
	buf []T
	ini int
	tam int
}

func (d *Deque[T]) crescer() {
	if d.tam < len(d.buf) {
		return
	}
	nova := make([]T, max(4, len(d.buf)*2))
	for i := 0; i < d.tam; i++ {
		nova[i] = d.buf[(d.ini+i)%len(d.buf)]
	}
	d.buf, d.ini = nova, 0
}

// AdicionarFim insere no fim.
func (d *Deque[T]) AdicionarFim(v T) {
	d.crescer()
	d.buf[(d.ini+d.tam)%len(d.buf)] = v
	d.tam++
}

// AdicionarInicio insere no início.
func (d *Deque[T]) AdicionarInicio(v T) {
	d.crescer()
	d.ini = (d.ini - 1 + len(d.buf)) % len(d.buf)
	d.buf[d.ini] = v
	d.tam++
}

// RemoverInicio remove e devolve o primeiro.
func (d *Deque[T]) RemoverInicio() (v T, ok bool) {
	if d.tam == 0 {
		return v, false
	}
	v = d.buf[d.ini]
	var zero T
	d.buf[d.ini] = zero
	d.ini = (d.ini + 1) % len(d.buf)
	d.tam--
	return v, true
}

// RemoverFim remove e devolve o último.
func (d *Deque[T]) RemoverFim() (v T, ok bool) {
	if d.tam == 0 {
		return v, false
	}
	i := (d.ini + d.tam - 1) % len(d.buf)
	v = d.buf[i]
	var zero T
	d.buf[i] = zero
	d.tam--
	return v, true
}

// Tamanho devolve a quantidade de itens.
func (d *Deque[T]) Tamanho() int { return d.tam }
