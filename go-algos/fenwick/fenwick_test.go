package fenwick

import (
	"math/rand"
	"testing"
)

func TestIntervalo(t *testing.T) {
	a := De([]int{3, 2, -1, 6, 5, 4, -3, 3, 7, 2, 3})
	casos := []struct{ l, r, want int }{
		{0, 10, 31},
		{0, 0, 3},
		{2, 4, 10},
		{5, 5, 4},
		{4, 2, 0},
		{3, 100, 27},
	}
	for _, c := range casos {
		if got := a.Intervalo(c.l, c.r); got != c.want {
			t.Errorf("Intervalo(%d,%d)=%d, esperado %d", c.l, c.r, got, c.want)
		}
	}
}

func TestSomar(t *testing.T) {
	a := Nova(5)
	a.Somar(0, 5)
	a.Somar(4, 7)
	a.Somar(2, -2)
	if got := a.Intervalo(0, 4); got != 10 {
		t.Errorf("total=%d", got)
	}
	if got := a.Prefixo(1); got != 5 {
		t.Errorf("prefixo=%d", got)
	}
	if got := Nova(0).Prefixo(0); got != 0 {
		t.Errorf("vazia=%d", got)
	}
}

func TestAleatorio(t *testing.T) {
	r := rand.New(rand.NewSource(3))
	n := 200
	ref := make([]int, n)
	a := Nova(n)
	for k := 0; k < 2000; k++ {
		i, d := r.Intn(n), r.Intn(21)-10
		ref[i] += d
		a.Somar(i, d)
		l, rr := r.Intn(n), r.Intn(n)
		if l > rr {
			l, rr = rr, l
		}
		s := 0
		for x := l; x <= rr; x++ {
			s += ref[x]
		}
		if got := a.Intervalo(l, rr); got != s {
			t.Fatalf("Intervalo(%d,%d)=%d, esperado %d", l, rr, got, s)
		}
	}
}

func BenchmarkSomar(b *testing.B) {
	a := Nova(1 << 16)
	for i := 0; i < b.N; i++ {
		a.Somar(i&0xffff, 1)
	}
}
