// Pacote trie implementa uma árvore de prefixos (trie) genérica sobre runas.
package trie

import "sort"

type no[V any] struct {
	filhos map[rune]*no[V]
	valor  V
	final  bool
}

func novoNo[V any]() *no[V] { return &no[V]{filhos: map[rune]*no[V]{}} }

// Trie mapeia strings para valores e permite busca por prefixo.
type Trie[V any] struct {
	raiz *no[V]
	tam  int
}

// Nova cria uma trie vazia.
func Nova[V any]() *Trie[V] { return &Trie[V]{raiz: novoNo[V]()} }

// Tamanho devolve a quantidade de chaves.
func (t *Trie[V]) Tamanho() int { return t.tam }

// Inserir associa chave a valor; devolve true se a chave era nova.
// A chave vazia é válida.
func (t *Trie[V]) Inserir(chave string, valor V) bool {
	n := t.raiz
	for _, r := range chave {
		f, ok := n.filhos[r]
		if !ok {
			f = novoNo[V]()
			n.filhos[r] = f
		}
		n = f
	}
	novo := !n.final
	n.final, n.valor = true, valor
	if novo {
		t.tam++
	}
	return novo
}

func (t *Trie[V]) achar(prefixo string) *no[V] {
	n := t.raiz
	for _, r := range prefixo {
		n = n.filhos[r]
		if n == nil {
			return nil
		}
	}
	return n
}

// Buscar devolve o valor associado à chave exata.
func (t *Trie[V]) Buscar(chave string) (v V, ok bool) {
	if n := t.achar(chave); n != nil && n.final {
		return n.valor, true
	}
	return v, false
}

// TemPrefixo informa se alguma chave começa com prefixo.
func (t *Trie[V]) TemPrefixo(prefixo string) bool { return t.achar(prefixo) != nil }

// Remover apaga a chave e poda os nós que ficaram inúteis.
func (t *Trie[V]) Remover(chave string) bool {
	runas := []rune(chave)
	caminho := make([]*no[V], 0, len(runas)+1)
	n := t.raiz
	caminho = append(caminho, n)
	for _, r := range runas {
		n = n.filhos[r]
		if n == nil {
			return false
		}
		caminho = append(caminho, n)
	}
	if !n.final {
		return false
	}
	var zero V
	n.final, n.valor = false, zero
	t.tam--
	for i := len(runas); i > 0; i-- {
		atual := caminho[i]
		if atual.final || len(atual.filhos) > 0 {
			break
		}
		delete(caminho[i-1].filhos, runas[i-1])
	}
	return true
}

// ComPrefixo devolve, em ordem alfabética, todas as chaves que começam com prefixo.
func (t *Trie[V]) ComPrefixo(prefixo string) []string {
	r := []string{}
	n := t.achar(prefixo)
	if n == nil {
		return r
	}
	var coleta func(n *no[V], atual []rune)
	coleta = func(n *no[V], atual []rune) {
		if n.final {
			r = append(r, string(atual))
		}
		rs := make([]rune, 0, len(n.filhos))
		for k := range n.filhos {
			rs = append(rs, k)
		}
		sort.Slice(rs, func(i, j int) bool { return rs[i] < rs[j] })
		for _, k := range rs {
			coleta(n.filhos[k], append(atual, k))
		}
	}
	coleta(n, []rune(prefixo))
	return r
}
