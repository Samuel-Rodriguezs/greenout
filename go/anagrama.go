package lab

import "unicode"

// AnagramaSao informa se a e b são anagramas, ignorando espaços,
// pontuação e maiúsculas/minúsculas.
func AnagramaSao(a, b string) bool {
	contagem := make(map[rune]int)
	for _, r := range a {
		if unicode.IsLetter(r) || unicode.IsDigit(r) {
			contagem[unicode.ToLower(r)]++
		}
	}
	for _, r := range b {
		if unicode.IsLetter(r) || unicode.IsDigit(r) {
			contagem[unicode.ToLower(r)]--
		}
	}
	for _, v := range contagem {
		if v != 0 {
			return false
		}
	}
	return true
}
