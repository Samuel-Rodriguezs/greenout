package lab

import "cmp"

// OrdenarQuick devolve uma cópia ordenada de dados usando quicksort
// (pivô mediano de três, partição de Lomuto). Não altera a entrada.
func OrdenarQuick[T cmp.Ordered](dados []T) []T {
	copia := make([]T, len(dados))
	copy(copia, dados)
	quickRec(copia)
	return copia
}

func quickRec[T cmp.Ordered](a []T) {
	for len(a) > 1 {
		meio, ult := len(a)/2, len(a)-1
		// mediano de três vai para a última posição como pivô
		if a[meio] < a[0] {
			a[meio], a[0] = a[0], a[meio]
		}
		if a[ult] < a[0] {
			a[ult], a[0] = a[0], a[ult]
		}
		if a[meio] < a[ult] {
			a[meio], a[ult] = a[ult], a[meio]
		}
		pivo := a[ult]
		i := 0
		for j := 0; j < ult; j++ {
			if a[j] < pivo {
				a[i], a[j] = a[j], a[i]
				i++
			}
		}
		a[i], a[ult] = a[ult], a[i]
		// recursão no menor lado, laço no maior (pilha O(log n))
		if i < len(a)-i-1 {
			quickRec(a[:i])
			a = a[i+1:]
		} else {
			quickRec(a[i+1:])
			a = a[:i]
		}
	}
}

// OrdenarMerge devolve uma cópia ordenada de dados usando mergesort (estável).
func OrdenarMerge[T cmp.Ordered](dados []T) []T {
	if len(dados) <= 1 {
		copia := make([]T, len(dados))
		copy(copia, dados)
		return copia
	}
	meio := len(dados) / 2
	esq := OrdenarMerge(dados[:meio])
	dir := OrdenarMerge(dados[meio:])
	saida := make([]T, 0, len(dados))
	i, j := 0, 0
	for i < len(esq) && j < len(dir) {
		if dir[j] < esq[i] {
			saida = append(saida, dir[j])
			j++
		} else {
			saida = append(saida, esq[i])
			i++
		}
	}
	saida = append(saida, esq[i:]...)
	return append(saida, dir[j:]...)
}
