package bplustree

import (
	"math/rand"
	"sort"
	"testing"
)

func TestOrdemInvalida(t *testing.T) {
	for _, m := range []int{-1, 0, 2} {
		if _, err := Nova[int, int](m); err != ErrOrdemInvalida {
			t.Fatalf("ordem %d: err = %v", m, err)
		}
	}
}

func TestInserirBuscar(t *testing.T) {
	casos := []struct {
		nome string
		m    int
		ks   []int
	}{
		{"crescente m=3", 3, seq(0, 300, 1)},
		{"decrescente m=4", 4, seq(300, 0, -1)},
		{"aleatoria m=3", 3, rand.New(rand.NewSource(1)).Perm(400)},
		{"aleatoria m=5", 5, rand.New(rand.NewSource(2)).Perm(400)},
		{"aleatoria m=32", 32, rand.New(rand.NewSource(3)).Perm(2000)},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			a, _ := Nova[int, int](c.m)
			for _, k := range c.ks {
				if !a.Inserir(k, k*2) {
					t.Fatalf("%d deveria ser nova", k)
				}
			}
			if err := a.Validar(); err != nil {
				t.Fatal(err)
			}
			for _, k := range c.ks {
				if v, ok := a.Buscar(k); !ok || v != k*2 {
					t.Fatalf("buscar %d = (%d,%v)", k, v, ok)
				}
			}
			if _, ok := a.Buscar(-5); ok {
				t.Fatal("chave inexistente achada")
			}
			if a.Inserir(c.ks[0], 7) {
				t.Fatal("reinserir não deveria contar como nova")
			}
			if v, _ := a.Buscar(c.ks[0]); v != 7 {
				t.Fatal("valor não substituído")
			}
		})
	}
}

func seq(de, ate, passo int) []int {
	var r []int
	for i := de; i != ate; i += passo {
		r = append(r, i)
	}
	return r
}

func TestIntervalo(t *testing.T) {
	a, _ := Nova[int, string](4)
	for i := 0; i < 100; i += 2 { // só pares
		a.Inserir(i, "v")
	}
	casos := []struct {
		nome    string
		de, ate int
		quer    []int
	}{
		{"meio", 10, 20, []int{10, 12, 14, 16, 18}},
		{"limite inferior ausente", 11, 17, []int{12, 14, 16}},
		{"vazio", 20, 20, nil},
		{"invertido", 30, 10, nil},
		{"antes do inicio", -50, 5, []int{0, 2, 4}},
		{"depois do fim", 95, 1000, []int{96, 98}},
		{"fora", 500, 600, nil},
		{"tudo", -1, 1000, seq(0, 100, 2)},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			var got []int
			a.Intervalo(c.de, c.ate, func(k int, _ string) bool { got = append(got, k); return true })
			if len(got) != len(c.quer) {
				t.Fatalf("got %v, quer %v", got, c.quer)
			}
			for i := range got {
				if got[i] != c.quer[i] {
					t.Fatalf("got %v, quer %v", got, c.quer)
				}
			}
		})
	}
	var n int
	a.Intervalo(0, 100, func(int, string) bool { n++; return n < 3 })
	if n != 3 {
		t.Fatalf("interrupção: visitou %d", n)
	}
}

func TestRemoverTudo(t *testing.T) {
	for _, m := range []int{3, 4, 5, 8, 33} {
		for _, ordem := range []string{"crescente", "decrescente", "aleatoria"} {
			a, _ := Nova[int, int](m)
			n := 500
			for i := 0; i < n; i++ {
				a.Inserir(i, i)
			}
			ks := rand.New(rand.NewSource(int64(m))).Perm(n)
			switch ordem {
			case "crescente":
				sort.Ints(ks)
			case "decrescente":
				sort.Sort(sort.Reverse(sort.IntSlice(ks)))
			}
			for i, k := range ks {
				if !a.Remover(k) {
					t.Fatalf("m=%d %s: remover %d falhou", m, ordem, k)
				}
				if a.Remover(k) {
					t.Fatalf("m=%d %s: remover %d de novo", m, ordem, k)
				}
				if err := a.Validar(); err != nil {
					t.Fatalf("m=%d %s após %d remoções: %v", m, ordem, i+1, err)
				}
			}
			if a.Tamanho() != 0 || a.Altura() != 1 {
				t.Fatalf("m=%d %s: deveria estar vazia", m, ordem)
			}
		}
	}
}

func TestContraMapaAleatorio(t *testing.T) {
	r := rand.New(rand.NewSource(7))
	a, _ := Nova[int, int](4)
	ref := map[int]int{}
	for i := 0; i < 30000; i++ {
		k := r.Intn(500)
		if r.Intn(3) < 2 {
			_, existia := ref[k]
			if a.Inserir(k, i) == existia {
				t.Fatalf("inserir %d inconsistente", k)
			}
			ref[k] = i
		} else {
			_, existia := ref[k]
			if a.Remover(k) != existia {
				t.Fatalf("remover %d inconsistente", k)
			}
			delete(ref, k)
		}
		if i%700 == 0 {
			if err := a.Validar(); err != nil {
				t.Fatalf("passo %d: %v", i, err)
			}
		}
	}
	var chaves []int
	a.Percorrer(func(k, v int) bool {
		if ref[k] != v {
			t.Fatalf("valor de %d diverge", k)
		}
		chaves = append(chaves, k)
		return true
	})
	if len(chaves) != len(ref) || !sort.IntsAreSorted(chaves) {
		t.Fatal("percurso inconsistente com o mapa")
	}
}

func TestVazia(t *testing.T) {
	a, _ := Nova[string, int](3)
	if _, ok := a.Buscar("x"); ok || a.Remover("x") {
		t.Fatal("operações em árvore vazia")
	}
	a.Intervalo("a", "z", func(string, int) bool { t.Fatal("não deveria visitar"); return true })
	a.Percorrer(func(string, int) bool { t.Fatal("não deveria visitar"); return true })
}
