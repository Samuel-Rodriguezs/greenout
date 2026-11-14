// Pacote fenwick implementa a árvore de Fenwick (BIT) para somas de prefixo.
package fenwick

// Arvore guarda somas parciais; índices externos começam em 0.
type Arvore struct {
	bit []int
}

// Nova cria uma árvore de n posições zeradas.
func Nova(n int) *Arvore { return &Arvore{bit: make([]int, n+1)} }

// De constrói a árvore a partir de valores em O(n).
func De(valores []int) *Arvore {
	a := Nova(len(valores))
	copy(a.bit[1:], valores)
	for i := 1; i < len(a.bit); i++ {
		if j := i + (i & -i); j < len(a.bit) {
			a.bit[j] += a.bit[i]
		}
	}
	return a
}

// Tamanho devolve o número de posições.
func (a *Arvore) Tamanho() int { return len(a.bit) - 1 }

// Somar adiciona delta à posição i.
func (a *Arvore) Somar(i, delta int) {
	for i++; i < len(a.bit); i += i & -i {
		a.bit[i] += delta
	}
}

// Prefixo devolve a soma das posições [0, i].
func (a *Arvore) Prefixo(i int) int {
	if i >= a.Tamanho() {
		i = a.Tamanho() - 1
	}
	s := 0
	for i++; i > 0; i -= i & -i {
		s += a.bit[i]
	}
	return s
}

// Intervalo devolve a soma das posições [l, r] (inclusive).
func (a *Arvore) Intervalo(l, r int) int {
	if l > r {
		return 0
	}
	return a.Prefixo(r) - a.Prefixo(l-1)
}
