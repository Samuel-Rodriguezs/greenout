package segtree

import (
	"math/rand"
	"testing"
)

func TestBasico(t *testing.T) {
	a := Nova([]int{1, 2, 3, 4, 5})
	if got := a.Consultar(0, 4); got != 15 {
		t.Errorf("total=%d", got)
	}
	a.Somar(1, 3, 10)
	casos := []struct{ l, r, want int }{
		{0, 4, 45},
		{1, 1, 12},
		{2, 3, 27},
		{0, 0, 1},
		{4, 4, 5},
		{3, 1, 0},
		{-5, 100, 45},
	}
	for _, c := range casos {
		if got := a.Consultar(c.l, c.r); got != c.want {
			t.Errorf("Consultar(%d,%d)=%d, esperado %d", c.l, c.r, got, c.want)
		}
	}
}

func TestVazio(t *testing.T) {
	a := Nova(nil)
	a.Somar(0, 3, 1)
	if got := a.Consultar(0, 3); got != 0 {
		t.Errorf("vazia=%d", got)
	}
}

func TestAleatorio(t *testing.T) {
	r := rand.New(rand.NewSource(4))
	n := 100
	ref := make([]int, n)
	for i := range ref {
		ref[i] = r.Intn(10)
	}
	a := Nova(append([]int(nil), ref...))
	for k := 0; k < 2000; k++ {
		l, rr := r.Intn(n), r.Intn(n)
		if l > rr {
			l, rr = rr, l
		}
		if r.Intn(2) == 0 {
			d := r.Intn(21) - 10
			a.Somar(l, rr, d)
			for x := l; x <= rr; x++ {
				ref[x] += d
			}
			continue
		}
		s := 0
		for x := l; x <= rr; x++ {
			s += ref[x]
		}
		if got := a.Consultar(l, rr); got != s {
			t.Fatalf("Consultar(%d,%d)=%d, esperado %d", l, rr, got, s)
		}
	}
}
