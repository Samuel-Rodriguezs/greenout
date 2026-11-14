package lab

import "unicode"

// PalindromoEh informa se o texto é palíndromo, ignorando espaços,
// pontuação e diferença entre maiúsculas e minúsculas (suporta runes).
func PalindromoEh(texto string) bool {
	var letras []rune
	for _, r := range texto {
		if unicode.IsLetter(r) || unicode.IsDigit(r) {
			letras = append(letras, unicode.ToLower(r))
		}
	}
	for i, j := 0, len(letras)-1; i < j; i, j = i+1, j-1 {
		if letras[i] != letras[j] {
			return false
		}
	}
	return true
}
