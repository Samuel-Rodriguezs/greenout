// Pacote lis encontra a maior subsequência estritamente crescente em O(n log n).
package lis

import "sort"

// Sequencia devolve uma maior subsequência estritamente crescente de a.
func Sequencia(a []int) []int {
	if len(a) == 0 {
		return nil
	}
	// caudas[k] = índice do menor valor final de uma subsequência de tamanho k+1.
	var caudas []int
	pai := make([]int, len(a))
	for i, x := range a {
		k := sort.Search(len(caudas), func(j int) bool { return a[caudas[j]] >= x })
		if k > 0 {
			pai[i] = caudas[k-1]
		} else {
			pai[i] = -1
		}
		if k == len(caudas) {
			caudas = append(caudas, i)
		} else {
			caudas[k] = i
		}
	}
	res := make([]int, len(caudas))
	for i, k := len(caudas)-1, caudas[len(caudas)-1]; i >= 0; i, k = i-1, pai[k] {
		res[i] = a[k]
	}
	return res
}

// Tamanho devolve apenas o comprimento da LIS.
func Tamanho(a []int) int { return len(Sequencia(a)) }
