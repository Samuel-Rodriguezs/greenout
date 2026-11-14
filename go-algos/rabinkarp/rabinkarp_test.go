package rabinkarp

import (
	"math/rand"
	"reflect"
	"strings"
	"testing"
)

func TestBuscar(t *testing.T) {
	casos := []struct {
		nome string
		s, p string
		want []int
	}{
		{"simples", "GEEKS FOR GEEKS", "GEEKS", []int{0, 10}},
		{"sobrepostas", "aaaaa", "aaa", []int{0, 1, 2}},
		{"nenhuma", "abcdef", "gh", nil},
		{"padrão vazio", "abc", "", nil},
		{"padrão maior", "ab", "abc", nil},
		{"tamanho um", "banana", "a", []int{1, 3, 5}},
		{"igual", "abc", "abc", []int{0}},
		{"final", "xyzabc", "abc", []int{3}},
		{"utf8 por bytes", "ação ação", "ção", []int{1, 8}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := Buscar(c.s, c.p); !reflect.DeepEqual(got, c.want) {
				t.Errorf("got %v, esperado %v", got, c.want)
			}
		})
	}
}

func TestAleatorioContraNaive(t *testing.T) {
	r := rand.New(rand.NewSource(6))
	for k := 0; k < 500; k++ {
		var sb strings.Builder
		for i := r.Intn(60); i > 0; i-- {
			sb.WriteByte(byte('a' + r.Intn(2)))
		}
		s := sb.String()
		p := strings.Repeat("a", 1+r.Intn(3)) + strings.Repeat("b", r.Intn(2))
		var want []int
		for i := 0; i+len(p) <= len(s); i++ {
			if s[i:i+len(p)] == p {
				want = append(want, i)
			}
		}
		if got := Buscar(s, p); !reflect.DeepEqual(got, want) {
			t.Fatalf("Buscar(%q,%q)=%v, esperado %v", s, p, got, want)
		}
	}
}
