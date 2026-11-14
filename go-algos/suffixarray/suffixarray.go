// Pacote suffixarray constrói um vetor de sufixos simples (ordenação direta,
// O(n^2 log n) no pior caso) com LCP de Kasai e busca binária de padrões.
package suffixarray

import (
	"sort"
	"strings"
)

// Construir devolve os índices iniciais dos sufixos de s em ordem lexicográfica.
func Construir(s string) []int {
	sa := make([]int, len(s))
	for i := range sa {
		sa[i] = i
	}
	sort.Slice(sa, func(a, b int) bool { return s[sa[a]:] < s[sa[b]:] })
	return sa
}

// LCP devolve lcp onde lcp[i] é o maior prefixo comum entre os sufixos sa[i-1]
// e sa[i] (lcp[0] = 0), pelo algoritmo de Kasai em O(n).
func LCP(s string, sa []int) []int {
	n := len(s)
	rank := make([]int, n)
	for i, p := range sa {
		rank[p] = i
	}
	lcp := make([]int, n)
	for i, h := 0, 0; i < n; i++ {
		if rank[i] == 0 {
			h = 0
			continue
		}
		j := sa[rank[i]-1]
		for i+h < n && j+h < n && s[i+h] == s[j+h] {
			h++
		}
		lcp[rank[i]] = h
		if h > 0 {
			h--
		}
	}
	return lcp
}

// Buscar devolve, em ordem crescente, as posições de p em s usando o vetor
// de sufixos sa. Padrão vazio não tem ocorrências.
func Buscar(s string, sa []int, p string) []int {
	if p == "" {
		return nil
	}
	ini := sort.Search(len(sa), func(i int) bool { return s[sa[i]:] >= p })
	var res []int
	for i := ini; i < len(sa) && strings.HasPrefix(s[sa[i]:], p); i++ {
		res = append(res, sa[i])
	}
	sort.Ints(res)
	return res
}
