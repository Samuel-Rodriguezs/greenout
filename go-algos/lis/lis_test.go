package lis

import (
	"math/rand"
	"testing"
)

func forcaBruta(a []int) int {
	dp := make([]int, len(a))
	melhor := 0
	for i := range a {
		dp[i] = 1
		for j := 0; j < i; j++ {
			if a[j] < a[i] && dp[j]+1 > dp[i] {
				dp[i] = dp[j] + 1
			}
		}
		melhor = max(melhor, dp[i])
	}
	return melhor
}

func ehSubsequenciaCrescente(sub, a []int) bool {
	j := 0
	for i := range a {
		if j < len(sub) && a[i] == sub[j] {
			j++
		}
	}
	if j != len(sub) {
		return false
	}
	for i := 1; i < len(sub); i++ {
		if sub[i-1] >= sub[i] {
			return false
		}
	}
	return true
}

func TestTamanho(t *testing.T) {
	casos := []struct {
		nome string
		a    []int
		want int
	}{
		{"clássico", []int{10, 9, 2, 5, 3, 7, 101, 18}, 4},
		{"vazio", nil, 0},
		{"único", []int{7}, 1},
		{"todos iguais", []int{2, 2, 2, 2}, 1},
		{"decrescente", []int{5, 4, 3, 2, 1}, 1},
		{"crescente", []int{1, 2, 3, 4, 5}, 5},
		{"negativos", []int{-3, -1, -2, 0, -5, 4}, 4},
		{"leetcode", []int{0, 1, 0, 3, 2, 3}, 4},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := Tamanho(c.a); got != c.want {
				t.Errorf("Tamanho=%d, esperado %d", got, c.want)
			}
			if s := Sequencia(c.a); !ehSubsequenciaCrescente(s, c.a) {
				t.Errorf("sequência inválida %v", s)
			}
		})
	}
}

func TestAleatorio(t *testing.T) {
	r := rand.New(rand.NewSource(1))
	for i := 0; i < 300; i++ {
		a := make([]int, r.Intn(40))
		for j := range a {
			a[j] = r.Intn(20)
		}
		s := Sequencia(a)
		if len(s) != forcaBruta(a) || !ehSubsequenciaCrescente(s, a) {
			t.Fatalf("falha em %v: %v", a, s)
		}
	}
}

func BenchmarkSequencia(b *testing.B) {
	r := rand.New(rand.NewSource(2))
	a := make([]int, 10000)
	for i := range a {
		a[i] = r.Int()
	}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		Sequencia(a)
	}
}
