package lab

// LevenshteinDistancia calcula a distância de edição (inserção, remoção e
// substituição) entre a e b, operando sobre runes.
func LevenshteinDistancia(a, b string) int {
	ra, rb := []rune(a), []rune(b)
	anterior := make([]int, len(rb)+1)
	atual := make([]int, len(rb)+1)
	for j := range anterior {
		anterior[j] = j
	}
	for i := 1; i <= len(ra); i++ {
		atual[0] = i
		for j := 1; j <= len(rb); j++ {
			custo := 1
			if ra[i-1] == rb[j-1] {
				custo = 0
			}
			atual[j] = min(anterior[j]+1, atual[j-1]+1, anterior[j-1]+custo)
		}
		anterior, atual = atual, anterior
	}
	return anterior[len(rb)]
}
