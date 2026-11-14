package sparsetable

import (
	"math/rand"
	"testing"
)

func TestMinimo(t *testing.T) {
	s := Nova([]int{7, 2, 3, 0, 5, 10, 3, 12, 18})
	casos := []struct {
		l, r int
		want int
		ok   bool
	}{
		{0, 4, 0, true},
		{4, 7, 3, true},
		{7, 8, 12, true},
		{5, 5, 10, true},
		{0, 8, 0, true},
		{3, 2, 0, false},
		{-1, 2, 0, false},
		{0, 9, 0, false},
	}
	for _, c := range casos {
		got, ok := s.Minimo(c.l, c.r)
		if ok != c.ok || (ok && got != c.want) {
			t.Errorf("Minimo(%d,%d)=(%d,%v), esperado (%d,%v)", c.l, c.r, got, ok, c.want, c.ok)
		}
	}
}

func TestVazia(t *testing.T) {
	if _, ok := Nova(nil).Minimo(0, 0); ok {
		t.Error("tabela vazia não deveria responder")
	}
}

func TestAleatorio(t *testing.T) {
	r := rand.New(rand.NewSource(5))
	for n := 1; n <= 40; n++ {
		a := make([]int, n)
		for i := range a {
			a[i] = r.Intn(50) - 25
		}
		s := Nova(a)
		for l := 0; l < n; l++ {
			m := a[l]
			for rr := l; rr < n; rr++ {
				m = min(m, a[rr])
				if got, _ := s.Minimo(l, rr); got != m {
					t.Fatalf("n=%d Minimo(%d,%d)=%d, esperado %d", n, l, rr, got, m)
				}
			}
		}
	}
}
