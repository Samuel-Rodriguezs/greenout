package lab

import (
	"strings"
	"unicode"
)

// PalavrasContar conta a frequência de cada palavra do texto, ignorando
// maiúsculas/minúsculas e pontuação. Apóstrofo e hífen internos são mantidos.
func PalavrasContar(texto string) map[string]int {
	campos := strings.FieldsFunc(texto, func(r rune) bool {
		return !unicode.IsLetter(r) && !unicode.IsDigit(r) && r != '-' && r != '\''
	})
	contagem := make(map[string]int)
	for _, c := range campos {
		p := strings.ToLower(strings.Trim(c, "-'"))
		if p != "" {
			contagem[p]++
		}
	}
	return contagem
}
