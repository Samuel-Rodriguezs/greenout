package manacher

import (
	"math/rand"
	"testing"
)

func ehPalindromo(s string) bool {
	r := []rune(s)
	for i, j := 0, len(r)-1; i < j; i, j = i+1, j-1 {
		if r[i] != r[j] {
			return false
		}
	}
	return true
}

func contarNaive(s string) (int, int) {
	r := []rune(s)
	total, maior := 0, 0
	for i := range r {
		for j := i; j < len(r); j++ {
			if ehPalindromo(string(r[i : j+1])) {
				total++
				maior = max(maior, j-i+1)
			}
		}
	}
	return total, maior
}

func TestMaiorPalindromo(t *testing.T) {
	casos := []struct {
		nome string
		s    string
		want []string // alternativas aceitáveis
	}{
		{"babad", "babad", []string{"bab"}},
		{"par", "cbbd", []string{"bb"}},
		{"vazio", "", []string{""}},
		{"único", "x", []string{"x"}},
		{"todo palíndromo", "racecar", []string{"racecar"}},
		{"sem repetição", "abcd", []string{"a"}},
		{"par grande", "xabbay", []string{"abba"}},
		{"unicode", "ábá", []string{"ábá"}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			got := MaiorPalindromo(c.s)
			for _, w := range c.want {
				if got == w {
					return
				}
			}
			t.Errorf("got %q, esperado %v", got, c.want)
		})
	}
}

func TestContar(t *testing.T) {
	casos := map[string]int{"": 0, "a": 1, "aaa": 6, "abc": 3, "abba": 6}
	for s, want := range casos {
		if got := Contar(s); got != want {
			t.Errorf("Contar(%q)=%d, esperado %d", s, got, want)
		}
	}
}

func TestAleatorioContraNaive(t *testing.T) {
	r := rand.New(rand.NewSource(7))
	for k := 0; k < 300; k++ {
		b := make([]byte, r.Intn(25))
		for i := range b {
			b[i] = byte('a' + r.Intn(3))
		}
		s := string(b)
		total, maior := contarNaive(s)
		if got := Contar(s); got != total {
			t.Fatalf("Contar(%q)=%d, esperado %d", s, got, total)
		}
		p := MaiorPalindromo(s)
		if len(p) != maior || !ehPalindromo(p) {
			t.Fatalf("MaiorPalindromo(%q)=%q, tamanho esperado %d", s, p, maior)
		}
	}
}
