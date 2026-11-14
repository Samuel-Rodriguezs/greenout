package kmp

import (
	"reflect"
	"strings"
	"testing"
)

func TestPrefixo(t *testing.T) {
	casos := []struct {
		p    string
		want []int
	}{
		{"abacaba", []int{0, 0, 1, 0, 1, 2, 3}},
		{"aaaa", []int{0, 1, 2, 3}},
		{"abcd", []int{0, 0, 0, 0}},
		{"a", []int{0}},
		{"", []int{}},
	}
	for _, c := range casos {
		if got := Prefixo(c.p); !reflect.DeepEqual(got, c.want) {
			t.Errorf("Prefixo(%q)=%v, esperado %v", c.p, got, c.want)
		}
	}
}

func TestBuscar(t *testing.T) {
	casos := []struct {
		nome string
		s, p string
		want []int
	}{
		{"simples", "abxabcabcaby", "abcaby", []int{6}},
		{"sobrepostas", "aaaaa", "aa", []int{0, 1, 2, 3}},
		{"várias", "ababababa", "aba", []int{0, 2, 4, 6}},
		{"sem ocorrência", "abcdef", "xyz", nil},
		{"padrão vazio", "abc", "", nil},
		{"texto vazio", "", "a", nil},
		{"padrão maior", "ab", "abc", nil},
		{"igual", "abc", "abc", []int{0}},
		{"final", "xxabc", "abc", []int{2}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := Buscar(c.s, c.p); !reflect.DeepEqual(got, c.want) {
				t.Errorf("got %v, esperado %v", got, c.want)
			}
		})
	}
}

func TestContraStrings(t *testing.T) {
	s := strings.Repeat("abcab", 50) + "abcabd"
	p := "abcabd"
	var want []int
	for i := 0; i+len(p) <= len(s); i++ {
		if s[i:i+len(p)] == p {
			want = append(want, i)
		}
	}
	if got := Buscar(s, p); !reflect.DeepEqual(got, want) {
		t.Errorf("got %v, esperado %v", got, want)
	}
}

func BenchmarkBuscar(b *testing.B) {
	s := strings.Repeat("a", 100000) + "b"
	p := strings.Repeat("a", 100) + "b"
	for i := 0; i < b.N; i++ {
		Buscar(s, p)
	}
}
