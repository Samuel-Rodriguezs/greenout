package lab

import "testing"

func TestAnagramaSao(t *testing.T) {
	casos := []struct {
		nome string
		a, b string
		want bool
	}{
		{"vazios", "", "", true},
		{"simples", "amor", "roma", true},
		{"maiusculas", "Listen", "Silent", true},
		{"espacos", "dormitory", "dirty room", true},
		{"diferentes", "abc", "abd", false},
		{"tamanhos diferentes", "aab", "ab", false},
		{"unicode", "ação", "oçãa", true},
		{"unicode diferente", "ação", "acao", false},
		{"vazio vs letra", "", "a", false},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := AnagramaSao(c.a, c.b); got != c.want {
				t.Fatalf("AnagramaSao(%q,%q) = %v", c.a, c.b, got)
			}
		})
	}
}
