package unionfind

import "testing"

func TestUnionFind(t *testing.T) {
	u := Novo(6)
	casos := []struct {
		a, b  int
		unido bool
		comps int
	}{
		{0, 1, true, 5},
		{1, 2, true, 4},
		{0, 2, false, 4},
		{3, 4, true, 3},
		{2, 4, true, 2},
		{5, 5, false, 2},
	}
	for _, c := range casos {
		if got := u.Unir(c.a, c.b); got != c.unido {
			t.Errorf("Unir(%d,%d)=%v, esperado %v", c.a, c.b, got, c.unido)
		}
		if u.Componentes != c.comps {
			t.Errorf("componentes=%d, esperado %d", u.Componentes, c.comps)
		}
	}
	if !u.Conectados(0, 3) {
		t.Error("0 e 3 deveriam estar conectados")
	}
	if u.Conectados(0, 5) {
		t.Error("0 e 5 não deveriam estar conectados")
	}
}

func TestVazio(t *testing.T) {
	if u := Novo(0); u.Componentes != 0 {
		t.Error("esperado 0 componentes")
	}
}

func TestCadeiaLonga(t *testing.T) {
	n := 100000
	u := Novo(n)
	for i := 1; i < n; i++ {
		u.Unir(i-1, i)
	}
	if u.Componentes != 1 || !u.Conectados(0, n-1) {
		t.Error("cadeia longa deveria formar um único conjunto")
	}
}

func BenchmarkUnir(b *testing.B) {
	u := Novo(b.N + 1)
	for i := 0; i < b.N; i++ {
		u.Unir(i, i+1)
	}
}
