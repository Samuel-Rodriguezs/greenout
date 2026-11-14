// Pacote lista implementa uma lista duplamente ligada genérica.
package lista

type no[T any] struct {
	valor      T
	prox, ante *no[T]
}

// Lista é uma lista duplamente ligada. O valor zero está pronto para uso.
type Lista[T any] struct {
	ini, fim *no[T]
	tam      int
}

// Tamanho devolve a quantidade de elementos.
func (l *Lista[T]) Tamanho() int { return l.tam }

// AdicionarFim insere no final.
func (l *Lista[T]) AdicionarFim(v T) {
	n := &no[T]{valor: v, ante: l.fim}
	if l.fim == nil {
		l.ini = n
	} else {
		l.fim.prox = n
	}
	l.fim = n
	l.tam++
}

// AdicionarInicio insere no começo.
func (l *Lista[T]) AdicionarInicio(v T) {
	n := &no[T]{valor: v, prox: l.ini}
	if l.ini == nil {
		l.fim = n
	} else {
		l.ini.ante = n
	}
	l.ini = n
	l.tam++
}

func (l *Lista[T]) desligar(n *no[T]) {
	if n.ante == nil {
		l.ini = n.prox
	} else {
		n.ante.prox = n.prox
	}
	if n.prox == nil {
		l.fim = n.ante
	} else {
		n.prox.ante = n.ante
	}
	l.tam--
}

// RemoverPrimeiro remove e devolve o primeiro elemento.
func (l *Lista[T]) RemoverPrimeiro() (v T, ok bool) {
	if l.ini == nil {
		return v, false
	}
	n := l.ini
	l.desligar(n)
	return n.valor, true
}

// RemoverUltimo remove e devolve o último elemento.
func (l *Lista[T]) RemoverUltimo() (v T, ok bool) {
	if l.fim == nil {
		return v, false
	}
	n := l.fim
	l.desligar(n)
	return n.valor, true
}

// RemoverSe remove a primeira ocorrência que satisfaz o predicado.
func (l *Lista[T]) RemoverSe(f func(T) bool) bool {
	for n := l.ini; n != nil; n = n.prox {
		if f(n.valor) {
			l.desligar(n)
			return true
		}
	}
	return false
}

// Buscar devolve o primeiro elemento que satisfaz o predicado.
func (l *Lista[T]) Buscar(f func(T) bool) (v T, ok bool) {
	for n := l.ini; n != nil; n = n.prox {
		if f(n.valor) {
			return n.valor, true
		}
	}
	return v, false
}

// Inverter inverte a lista no lugar.
func (l *Lista[T]) Inverter() {
	for n := l.ini; n != nil; n = n.ante { // após trocar, ante é o antigo prox
		n.prox, n.ante = n.ante, n.prox
	}
	l.ini, l.fim = l.fim, l.ini
}

// Itens devolve os elementos do início ao fim.
func (l *Lista[T]) Itens() []T {
	r := make([]T, 0, l.tam)
	for n := l.ini; n != nil; n = n.prox {
		r = append(r, n.valor)
	}
	return r
}
