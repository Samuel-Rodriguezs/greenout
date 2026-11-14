// Pacote lcs calcula a maior subsequência comum com reconstrução.
package lcs

// Tamanho devolve o comprimento da maior subsequência comum de a e b (em runas).
func Tamanho(a, b string) int {
	tab := tabela([]rune(a), []rune(b))
	return tab[len([]rune(a))][len([]rune(b))]
}

// Subsequencia devolve uma maior subsequência comum de a e b.
func Subsequencia(a, b string) string {
	x, y := []rune(a), []rune(b)
	tab := tabela(x, y)
	res := make([]rune, tab[len(x)][len(y)])
	k := len(res) - 1
	for i, j := len(x), len(y); i > 0 && j > 0; {
		switch {
		case x[i-1] == y[j-1]:
			res[k] = x[i-1]
			k--
			i--
			j--
		case tab[i-1][j] >= tab[i][j-1]:
			i--
		default:
			j--
		}
	}
	return string(res)
}

func tabela(x, y []rune) [][]int {
	tab := make([][]int, len(x)+1)
	for i := range tab {
		tab[i] = make([]int, len(y)+1)
	}
	for i := 1; i <= len(x); i++ {
		for j := 1; j <= len(y); j++ {
			if x[i-1] == y[j-1] {
				tab[i][j] = tab[i-1][j-1] + 1
			} else {
				tab[i][j] = max(tab[i-1][j], tab[i][j-1])
			}
		}
	}
	return tab
}
