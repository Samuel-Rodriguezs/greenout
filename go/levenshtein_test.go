package lab

import "testing"

func TestLevenshteinDistancia(t *testing.T) {
	casos := []struct {
		nome string
		a, b string
		want int
	}{
		{"ambos vazios", "", "", 0},
		{"a vazio", "", "abc", 3},
		{"b vazio", "abcd", "", 4},
		{"iguais", "golang", "golang", 0},
		{"classico", "kitten", "sitting", 3},
		{"substituicao", "casa", "cara", 1},
		{"insercao", "ab", "abc", 1},
		{"remocao", "abc", "ac", 1},
		{"unicode", "ação", "acao", 2},
		{"unicode runes", "é", "e", 1},
		{"totalmente diferentes", "abc", "xyz", 3},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := LevenshteinDistancia(c.a, c.b); got != c.want {
				t.Fatalf("got %d want %d", got, c.want)
			}
			if got := LevenshteinDistancia(c.b, c.a); got != c.want {
				t.Fatalf("simetria: got %d want %d", got, c.want)
			}
		})
	}
}
