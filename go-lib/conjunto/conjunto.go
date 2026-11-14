// Pacote conjunto implementa um conjunto genérico (set) não seguro para concorrência.
package conjunto

// Conjunto é um conjunto de elementos comparáveis.
type Conjunto[T comparable] struct {
	m map[T]struct{}
}

// Novo cria um conjunto com os itens informados.
func Novo[T comparable](itens ...T) *Conjunto[T] {
	c := &Conjunto[T]{m: make(map[T]struct{}, len(itens))}
	for _, i := range itens {
		c.m[i] = struct{}{}
	}
	return c
}

// Adicionar insere o item e informa se ele era novo.
func (c *Conjunto[T]) Adicionar(i T) bool {
	if _, ok := c.m[i]; ok {
		return false
	}
	c.m[i] = struct{}{}
	return true
}

// Remover retira o item e informa se ele existia.
func (c *Conjunto[T]) Remover(i T) bool {
	if _, ok := c.m[i]; !ok {
		return false
	}
	delete(c.m, i)
	return true
}

// Contem informa se o item pertence ao conjunto.
func (c *Conjunto[T]) Contem(i T) bool {
	_, ok := c.m[i]
	return ok
}

// Tamanho devolve a quantidade de elementos.
func (c *Conjunto[T]) Tamanho() int { return len(c.m) }

// Itens devolve os elementos em ordem não especificada.
func (c *Conjunto[T]) Itens() []T {
	r := make([]T, 0, len(c.m))
	for k := range c.m {
		r = append(r, k)
	}
	return r
}

// Uniao devolve um novo conjunto com os elementos de ambos.
func (c *Conjunto[T]) Uniao(o *Conjunto[T]) *Conjunto[T] {
	r := Novo(c.Itens()...)
	for k := range o.m {
		r.m[k] = struct{}{}
	}
	return r
}

// Intersecao devolve os elementos presentes em ambos.
func (c *Conjunto[T]) Intersecao(o *Conjunto[T]) *Conjunto[T] {
	r := Novo[T]()
	for k := range c.m {
		if o.Contem(k) {
			r.m[k] = struct{}{}
		}
	}
	return r
}

// Diferenca devolve os elementos de c que não estão em o.
func (c *Conjunto[T]) Diferenca(o *Conjunto[T]) *Conjunto[T] {
	r := Novo[T]()
	for k := range c.m {
		if !o.Contem(k) {
			r.m[k] = struct{}{}
		}
	}
	return r
}

// Igual informa se os dois conjuntos têm exatamente os mesmos elementos.
func (c *Conjunto[T]) Igual(o *Conjunto[T]) bool {
	if c.Tamanho() != o.Tamanho() {
		return false
	}
	for k := range c.m {
		if !o.Contem(k) {
			return false
		}
	}
	return true
}
