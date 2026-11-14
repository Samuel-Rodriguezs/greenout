package ordenacao

import (
	"math/rand"
	"slices"
	"testing"
)

type par struct {
	chave int
	ordem int // posição original, para verificar estabilidade
}

func TestOrdenarEstavelInteiros(t *testing.T) {
	casos := []struct {
		nome string
		in   []int
	}{
		{"nil", nil},
		{"vazio", []int{}},
		{"um", []int{1}},
		{"ordenado", []int{1, 2, 3, 4, 5}},
		{"inverso", []int{5, 4, 3, 2, 1}},
		{"iguais", []int{7, 7, 7, 7}},
		{"com negativos", []int{3, -1, 2, -5, 0}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			got := slices.Clone(c.in)
			OrdenarEstavel(got, func(a, b int) bool { return a < b })
			want := slices.Clone(c.in)
			slices.Sort(want)
			if !slices.Equal(got, want) {
				t.Fatalf("got %v want %v", got, want)
			}
		})
	}
}

func TestEstabilidade(t *testing.T) {
	// tamanhos acima e abaixo do limite de inserção, com poucas chaves distintas
	for _, n := range []int{5, 12, 13, 100, 1000} {
		r := rand.New(rand.NewSource(int64(n)))
		s := make([]par, n)
		for i := range s {
			s[i] = par{chave: r.Intn(5), ordem: i}
		}
		OrdenarEstavel(s, func(a, b par) bool { return a.chave < b.chave })
		for i := 1; i < n; i++ {
			a, b := s[i-1], s[i]
			if a.chave > b.chave || (a.chave == b.chave && a.ordem > b.ordem) {
				t.Fatalf("n=%d: instável ou fora de ordem em %d: %v %v", n, i, a, b)
			}
		}
	}
}

func TestOrdenarPor(t *testing.T) {
	type pessoa struct {
		nome  string
		idade int
	}
	s := []pessoa{{"ana", 30}, {"bia", 25}, {"caio", 30}, {"davi", 25}}
	OrdenarPor(s, func(p pessoa) int { return p.idade })
	want := []string{"bia", "davi", "ana", "caio"}
	for i, p := range s {
		if p.nome != want[i] {
			t.Fatalf("posição %d: %s want %s", i, p.nome, want[i])
		}
	}
}

func TestDescendente(t *testing.T) {
	s := []int{1, 3, 2}
	OrdenarEstavel(s, func(a, b int) bool { return a > b })
	if !slices.Equal(s, []int{3, 2, 1}) {
		t.Fatalf("got %v", s)
	}
}

func TestEstaOrdenado(t *testing.T) {
	menor := func(a, b int) bool { return a < b }
	casos := []struct {
		in   []int
		want bool
	}{
		{nil, true}, {[]int{1}, true}, {[]int{1, 1, 2}, true}, {[]int{2, 1}, false},
	}
	for _, c := range casos {
		if got := EstaOrdenado(c.in, menor); got != c.want {
			t.Errorf("EstaOrdenado(%v)=%v", c.in, got)
		}
	}
}

func TestGrandeAleatorio(t *testing.T) {
	r := rand.New(rand.NewSource(7))
	s := make([]int, 5000)
	for i := range s {
		s[i] = r.Intn(1000)
	}
	want := slices.Clone(s)
	slices.Sort(want)
	OrdenarEstavel(s, func(a, b int) bool { return a < b })
	if !slices.Equal(s, want) {
		t.Fatal("resultado diverge de slices.Sort")
	}
}
