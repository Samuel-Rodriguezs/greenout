package nrainhas

import "testing"

func TestContar(t *testing.T) {
	// Sequência OEIS A000170.
	esperado := []int{1, 1, 0, 0, 2, 10, 4, 40, 92, 352, 724}
	for n, want := range esperado {
		if got := Contar(n); got != want {
			t.Errorf("Contar(%d)=%d, esperado %d", n, got, want)
		}
	}
	if Contar(-1) != 0 {
		t.Error("n negativo deveria dar 0")
	}
}

func valida(sol []int) bool {
	for i := range sol {
		for j := i + 1; j < len(sol); j++ {
			if sol[i] == sol[j] || sol[j]-sol[i] == j-i || sol[i]-sol[j] == j-i {
				return false
			}
		}
	}
	return true
}

func TestUma(t *testing.T) {
	for n := 1; n <= 10; n++ {
		sol, ok := Uma(n)
		if n == 2 || n == 3 {
			if ok {
				t.Errorf("n=%d não tem solução", n)
			}
			continue
		}
		if !ok || len(sol) != n || !valida(sol) {
			t.Errorf("n=%d: solução inválida %v", n, sol)
		}
	}
	if sol, ok := Uma(4); !ok || sol[0] != 1 || sol[1] != 3 || sol[2] != 0 || sol[3] != 2 {
		t.Errorf("primeira solução de 4 deveria ser [1 3 0 2], veio %v", sol)
	}
	if _, ok := Uma(0); !ok {
		t.Error("n=0 tem a solução vazia")
	}
	if _, ok := Uma(-2); ok {
		t.Error("n negativo não tem solução")
	}
}

func BenchmarkContar8(b *testing.B) {
	for i := 0; i < b.N; i++ {
		Contar(8)
	}
}
