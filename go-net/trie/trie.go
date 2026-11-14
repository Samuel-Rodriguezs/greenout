// Pacote trie implementa uma trie binária de prefixos IPv4 para busca do
// prefixo mais longo (longest prefix match), como numa tabela de roteamento.
package trie

import (
	"greenout/net/cidr"
	"greenout/net/ipv4"
)

type no[V any] struct {
	filho [2]*no[V]
	tem   bool
	valor V
}

// Trie associa prefixos IPv4 a valores do tipo V. Não é seguro para uso concorrente.
type Trie[V any] struct {
	raiz *no[V]
	n    int
}

// Nova cria uma trie vazia.
func Nova[V any]() *Trie[V] { return &Trie[V]{raiz: &no[V]{}} }

func bit(ip ipv4.Endereco, i int) int { return int(ip>>(31-uint(i))) & 1 }

// Inserir associa v ao prefixo p, substituindo valor anterior se houver.
func (t *Trie[V]) Inserir(p cidr.Prefixo, v V) {
	atual := t.raiz
	for i := 0; i < p.Tam; i++ {
		b := bit(p.Base, i)
		if atual.filho[b] == nil {
			atual.filho[b] = &no[V]{}
		}
		atual = atual.filho[b]
	}
	if !atual.tem {
		t.n++
	}
	atual.tem, atual.valor = true, v
}

// Buscar devolve o prefixo mais específico que contém ip, com seu valor.
func (t *Trie[V]) Buscar(ip ipv4.Endereco) (cidr.Prefixo, V, bool) {
	var (
		melhor    *no[V]
		melhorTam int
	)
	atual := t.raiz
	for i := 0; ; i++ {
		if atual.tem {
			melhor, melhorTam = atual, i
		}
		if i == 32 {
			break
		}
		atual = atual.filho[bit(ip, i)]
		if atual == nil {
			break
		}
	}
	if melhor == nil {
		var zero V
		return cidr.Prefixo{}, zero, false
	}
	return cidr.Novo(ip, melhorTam), melhor.valor, true
}

// Obter devolve o valor associado exatamente ao prefixo p.
func (t *Trie[V]) Obter(p cidr.Prefixo) (V, bool) {
	atual := t.raiz
	for i := 0; i < p.Tam && atual != nil; i++ {
		atual = atual.filho[bit(p.Base, i)]
	}
	if atual == nil || !atual.tem {
		var zero V
		return zero, false
	}
	return atual.valor, true
}

// Remover apaga o prefixo p e poda os nós que ficarem inúteis. Devolve false
// se p não estava presente.
func (t *Trie[V]) Remover(p cidr.Prefixo) bool {
	removido := false
	var rec func(n *no[V], i int) bool // devolve true se n pode ser podado
	rec = func(n *no[V], i int) bool {
		if i == p.Tam {
			if !n.tem {
				return false
			}
			var zero V
			n.tem, n.valor = false, zero
			removido = true
		} else {
			b := bit(p.Base, i)
			f := n.filho[b]
			if f == nil {
				return false
			}
			if rec(f, i+1) {
				n.filho[b] = nil
			}
		}
		return !n.tem && n.filho[0] == nil && n.filho[1] == nil
	}
	rec(t.raiz, 0)
	if removido {
		t.n--
	}
	return removido
}

// Tamanho devolve a quantidade de prefixos armazenados.
func (t *Trie[V]) Tamanho() int { return t.n }

// Percorrer visita todos os prefixos em ordem crescente de endereço (e do
// mais genérico ao mais específico). Interrompe se f devolver false.
func (t *Trie[V]) Percorrer(f func(cidr.Prefixo, V) bool) {
	var rec func(n *no[V], base ipv4.Endereco, tam int) bool
	rec = func(n *no[V], base ipv4.Endereco, tam int) bool {
		if n.tem && !f(cidr.Prefixo{Base: base, Tam: tam}, n.valor) {
			return false
		}
		for b := 0; b < 2; b++ {
			if n.filho[b] != nil {
				prox := base | ipv4.Endereco(b)<<(31-uint(tam))
				if !rec(n.filho[b], prox, tam+1) {
					return false
				}
			}
		}
		return true
	}
	rec(t.raiz, 0, 0)
}
