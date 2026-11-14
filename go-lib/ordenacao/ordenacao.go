// Pacote ordenacao implementa ordenação estável genérica (merge sort).
package ordenacao

import "cmp"

const limiteInsercao = 12

// OrdenarEstavel ordena s no lugar. menor(a, b) deve indicar se a vem
// estritamente antes de b; elementos equivalentes mantêm a ordem original.
func OrdenarEstavel[T any](s []T, menor func(a, b T) bool) {
	if len(s) < 2 {
		return
	}
	aux := make([]T, len(s))
	ordenar(s, aux, menor)
}

// OrdenarPor ordena s de forma estável pela chave calculada.
func OrdenarPor[T any, K cmp.Ordered](s []T, chave func(T) K) {
	OrdenarEstavel(s, func(a, b T) bool { return chave(a) < chave(b) })
}

// EstaOrdenado informa se s já está em ordem segundo menor.
func EstaOrdenado[T any](s []T, menor func(a, b T) bool) bool {
	for i := 1; i < len(s); i++ {
		if menor(s[i], s[i-1]) {
			return false
		}
	}
	return true
}

func ordenar[T any](s, aux []T, menor func(a, b T) bool) {
	if len(s) <= limiteInsercao {
		insercao(s, menor)
		return
	}
	meio := len(s) / 2
	ordenar(s[:meio], aux[:meio], menor)
	ordenar(s[meio:], aux[meio:], menor)
	// já em ordem: nada a mesclar
	if !menor(s[meio], s[meio-1]) {
		return
	}
	copy(aux, s)
	i, j, k := 0, meio, 0
	for i < meio && j < len(s) {
		// só pega da direita se for estritamente menor: preserva estabilidade
		if menor(aux[j], aux[i]) {
			s[k] = aux[j]
			j++
		} else {
			s[k] = aux[i]
			i++
		}
		k++
	}
	for i < meio {
		s[k] = aux[i]
		i++
		k++
	}
	for j < len(s) {
		s[k] = aux[j]
		j++
		k++
	}
}

func insercao[T any](s []T, menor func(a, b T) bool) {
	for i := 1; i < len(s); i++ {
		for j := i; j > 0 && menor(s[j], s[j-1]); j-- {
			s[j], s[j-1] = s[j-1], s[j]
		}
	}
}
