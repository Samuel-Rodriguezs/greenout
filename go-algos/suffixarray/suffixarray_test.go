package suffixarray

import (
	"reflect"
	"testing"
)

func TestConstruirELCP(t *testing.T) {
	casos := []struct {
		s   string
		sa  []int
		lcp []int
	}{
		{"banana", []int{5, 3, 1, 0, 4, 2}, []int{0, 1, 3, 0, 0, 2}},
		{"aaaa", []int{3, 2, 1, 0}, []int{0, 1, 2, 3}},
		{"abc", []int{0, 1, 2}, []int{0, 0, 0}},
		{"a", []int{0}, []int{0}},
		{"", []int{}, []int{}},
	}
	for _, c := range casos {
		sa := Construir(c.s)
		if !reflect.DeepEqual(sa, c.sa) {
			t.Errorf("Construir(%q)=%v, esperado %v", c.s, sa, c.sa)
		}
		if lcp := LCP(c.s, sa); !reflect.DeepEqual(lcp, c.lcp) {
			t.Errorf("LCP(%q)=%v, esperado %v", c.s, lcp, c.lcp)
		}
	}
}

func TestBuscar(t *testing.T) {
	s := "banana"
	sa := Construir(s)
	casos := []struct {
		p    string
		want []int
	}{
		{"ana", []int{1, 3}},
		{"a", []int{1, 3, 5}},
		{"banana", []int{0}},
		{"nan", []int{2}},
		{"x", nil},
		{"bananas", nil},
		{"", nil},
	}
	for _, c := range casos {
		if got := Buscar(s, sa, c.p); !reflect.DeepEqual(got, c.want) {
			t.Errorf("Buscar(%q)=%v, esperado %v", c.p, got, c.want)
		}
	}
}
