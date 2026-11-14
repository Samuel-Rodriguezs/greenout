package zalgo

import (
	"reflect"
	"testing"
)

func TestZ(t *testing.T) {
	casos := []struct {
		s    string
		want []int
	}{
		{"aabxaab", []int{7, 1, 0, 0, 3, 1, 0}},
		{"aaaaa", []int{5, 4, 3, 2, 1}},
		{"abcd", []int{4, 0, 0, 0}},
		{"a", []int{1}},
		{"", []int{}},
		{"abababab", []int{8, 0, 6, 0, 4, 0, 2, 0}},
	}
	for _, c := range casos {
		if got := Z(c.s); !reflect.DeepEqual(got, c.want) {
			t.Errorf("Z(%q)=%v, esperado %v", c.s, got, c.want)
		}
	}
}

func TestBuscar(t *testing.T) {
	casos := []struct {
		nome string
		s, p string
		want []int
	}{
		{"simples", "GEEKS FOR GEEKS", "GEEK", []int{0, 10}},
		{"sobrepostas", "aaaa", "aa", []int{0, 1, 2}},
		{"nenhuma", "abc", "d", nil},
		{"padrão vazio", "abc", "", nil},
		{"padrão maior", "a", "ab", nil},
		{"inteiro", "abc", "abc", []int{0}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := Buscar(c.s, c.p); !reflect.DeepEqual(got, c.want) {
				t.Errorf("got %v, esperado %v", got, c.want)
			}
		})
	}
}
