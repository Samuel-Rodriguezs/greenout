package lcs

import "testing"

func ehSubsequencia(s, t string) bool {
	r := []rune(s)
	i := 0
	for _, c := range t {
		if i < len(r) && r[i] == c {
			i++
		}
	}
	return i == len(r)
}

func TestLCS(t *testing.T) {
	casos := []struct {
		nome string
		a, b string
		want int
	}{
		{"clássico", "AGGTAB", "GXTXAYB", 4},
		{"CLRS", "ABCBDAB", "BDCABA", 4},
		{"vazio a", "", "abc", 0},
		{"vazio b", "abc", "", 0},
		{"ambos vazios", "", "", 0},
		{"iguais", "golang", "golang", 6},
		{"disjuntas", "abc", "xyz", 0},
		{"unicode", "programação", "programar ação", 11},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := Tamanho(c.a, c.b); got != c.want {
				t.Errorf("Tamanho=%d, esperado %d", got, c.want)
			}
			s := Subsequencia(c.a, c.b)
			if len([]rune(s)) != c.want || !ehSubsequencia(s, c.a) || !ehSubsequencia(s, c.b) {
				t.Errorf("subsequência inválida %q", s)
			}
		})
	}
}

func TestSubsequenciaExata(t *testing.T) {
	if s := Subsequencia("AGGTAB", "GXTXAYB"); s != "GTAB" {
		t.Errorf("got %q, esperado GTAB", s)
	}
}
