package lab

import "cmp"

// BuscaBinariaIndice procura alvo em um slice ordenado de forma crescente.
// Devolve o índice e true se encontrado; caso contrário, -1 e false.
func BuscaBinariaIndice[T cmp.Ordered](ordenado []T, alvo T) (int, bool) {
	baixo, alto := 0, len(ordenado)-1
	for baixo <= alto {
		meio := baixo + (alto-baixo)/2
		switch c := cmp.Compare(ordenado[meio], alvo); {
		case c == 0:
			return meio, true
		case c < 0:
			baixo = meio + 1
		default:
			alto = meio - 1
		}
	}
	return -1, false
}
