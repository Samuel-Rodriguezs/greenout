package lab

import "container/list"

type entradaLRU[K comparable, V any] struct {
	chave K
	valor V
}

// CacheLRU é um cache de capacidade fixa que descarta o item menos
// recentemente usado. Não é seguro para uso concorrente.
type CacheLRU[K comparable, V any] struct {
	capacidade int
	ordem      *list.List // frente = mais recente
	indice     map[K]*list.Element
}

// NovoCacheLRU cria um cache; capacidade < 1 é ajustada para 1.
func NovoCacheLRU[K comparable, V any](capacidade int) *CacheLRU[K, V] {
	if capacidade < 1 {
		capacidade = 1
	}
	return &CacheLRU[K, V]{
		capacidade: capacidade,
		ordem:      list.New(),
		indice:     make(map[K]*list.Element),
	}
}

// Obter devolve o valor e marca a chave como mais recente.
func (c *CacheLRU[K, V]) Obter(chave K) (V, bool) {
	if el, ok := c.indice[chave]; ok {
		c.ordem.MoveToFront(el)
		return el.Value.(*entradaLRU[K, V]).valor, true
	}
	var zero V
	return zero, false
}

// Colocar insere ou atualiza a chave, removendo a mais antiga se necessário.
func (c *CacheLRU[K, V]) Colocar(chave K, valor V) {
	if el, ok := c.indice[chave]; ok {
		el.Value.(*entradaLRU[K, V]).valor = valor
		c.ordem.MoveToFront(el)
		return
	}
	if c.ordem.Len() >= c.capacidade {
		velho := c.ordem.Back()
		c.ordem.Remove(velho)
		delete(c.indice, velho.Value.(*entradaLRU[K, V]).chave)
	}
	c.indice[chave] = c.ordem.PushFront(&entradaLRU[K, V]{chave, valor})
}

// Tamanho devolve a quantidade de itens no cache.
func (c *CacheLRU[K, V]) Tamanho() int { return c.ordem.Len() }

// Chaves devolve as chaves da mais recente para a mais antiga.
func (c *CacheLRU[K, V]) Chaves() []K {
	saida := make([]K, 0, c.ordem.Len())
	for el := c.ordem.Front(); el != nil; el = el.Next() {
		saida = append(saida, el.Value.(*entradaLRU[K, V]).chave)
	}
	return saida
}
