// Pacote permutacoes gera permutações e combinações por backtracking.
package permutacoes

import "sort"

// Permutacoes devolve todas as permutações distintas de v em ordem
// lexicográfica (v não é alterado; elementos repetidos não geram duplicatas).
func Permutacoes(v []int) [][]int {
	ord := append([]int(nil), v...)
	sort.Ints(ord)
	usado := make([]bool, len(ord))
	atual := make([]int, 0, len(ord))
	var res [][]int
	var gera func()
	gera = func() {
		if len(atual) == len(ord) {
			res = append(res, append([]int{}, atual...))
			return
		}
		for i := range ord {
			if usado[i] || (i > 0 && ord[i] == ord[i-1] && !usado[i-1]) {
				continue
			}
			usado[i] = true
			atual = append(atual, ord[i])
			gera()
			atual = atual[:len(atual)-1]
			usado[i] = false
		}
	}
	gera()
	return res
}

// Combinacoes devolve todas as combinações de k números escolhidos de 1..n,
// em ordem lexicográfica.
func Combinacoes(n, k int) [][]int {
	if k < 0 || k > n {
		return nil
	}
	atual := make([]int, 0, k)
	var res [][]int
	var gera func(ini int)
	gera = func(ini int) {
		if len(atual) == k {
			res = append(res, append([]int{}, atual...))
			return
		}
		// poda: precisa sobrar elementos suficientes
		for x := ini; x <= n-(k-len(atual))+1; x++ {
			atual = append(atual, x)
			gera(x + 1)
			atual = atual[:len(atual)-1]
		}
	}
	gera(1)
	return res
}
