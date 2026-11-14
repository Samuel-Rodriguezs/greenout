package lab

import "testing"

func TestPalindromoEh(t *testing.T) {
	casos := []struct {
		nome  string
		texto string
		want  bool
	}{
		{"vazio", "", true},
		{"uma letra", "a", true},
		{"simples", "arara", true},
		{"frase", "A man, a plan, a canal: Panama", true},
		{"maiusculas", "Ovo", true},
		{"nao palindromo", "golang", false},
		{"unicode", "été", true},
		{"unicode japones", "たけやぶやけた", true},
		{"so pontuacao", "!?, .", true},
		{"numeros", "12321", true},
		{"numeros nao", "12345", false},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := PalindromoEh(c.texto); got != c.want {
				t.Fatalf("PalindromoEh(%q) = %v", c.texto, got)
			}
		})
	}
}
