package btree

import (
	"math/rand"
	"sort"
	"testing"
)

func TestGrauInvalido(t *testing.T) {
	for _, g := range []int{-1, 0, 1} {
		if _, err := Nova[int, int](g); err != ErrGrauInvalido {
			t.Fatalf("grau %d: err = %v", g, err)
		}
	}
}

func TestInserirBuscarOrdemEGrau(t *testing.T) {
	casos := []struct {
		nome   string
		grau   int
		chaves func(n int) []int
	}{
		{"crescente t=2", 2, func(n int) []int {
			r := make([]int, n)
			for i := range r {
				r[i] = i
			}
			return r
		}},
		{"decrescente t=3", 3, func(n int) []int {
			r := make([]int, n)
			for i := range r {
				r[i] = n - i
			}
			return r
		}},
		{"aleatoria t=2", 2, func(n int) []int { return rand.New(rand.NewSource(1)).Perm(n) }},
		{"aleatoria t=5", 5, func(n int) []int { return rand.New(rand.NewSource(2)).Perm(n) }},
		{"aleatoria t=16", 16, func(n int) []int { return rand.New(rand.NewSource(3)).Perm(n) }},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			a, _ := Nova[int, string](c.grau)
			ks := c.chaves(500)
			for _, k := range ks {
				if !a.Inserir(k, "v") {
					t.Fatalf("chave %d deveria ser nova", k)
				}
				if err := a.Validar(); err != nil {
					t.Fatalf("após inserir %d: %v", k, err)
				}
			}
			if a.Tamanho() != 500 {
				t.Fatalf("tamanho = %d", a.Tamanho())
			}
			for _, k := range ks {
				if _, ok := a.Buscar(k); !ok {
					t.Fatalf("chave %d não encontrada", k)
				}
			}
			if _, ok := a.Buscar(-1); ok {
				t.Fatal("chave inexistente encontrada")
			}
			var vistos []int
			a.Percorrer(func(k int, _ string) bool { vistos = append(vistos, k); return true })
			if !sort.IntsAreSorted(vistos) || len(vistos) != 500 {
				t.Fatal("percurso fora de ordem ou incompleto")
			}
		})
	}
}

func TestSubstituirValor(t *testing.T) {
	a, _ := Nova[int, string](2)
	for i := 0; i < 50; i++ {
		a.Inserir(i, "a")
	}
	for i := 0; i < 50; i++ {
		if a.Inserir(i, "b") {
			t.Fatalf("chave %d não deveria ser nova", i)
		}
	}
	if a.Tamanho() != 50 {
		t.Fatalf("tamanho = %d", a.Tamanho())
	}
	for i := 0; i < 50; i++ {
		if v, _ := a.Buscar(i); v != "b" {
			t.Fatalf("valor de %d = %q", i, v)
		}
	}
	if err := a.Validar(); err != nil {
		t.Fatal(err)
	}
}

func TestVazia(t *testing.T) {
	a, _ := Nova[string, int](3)
	if _, ok := a.Buscar("x"); ok {
		t.Fatal("busca em vazia")
	}
	if a.Remover("x") {
		t.Fatal("remover de vazia")
	}
	if a.Altura() != 1 || a.Tamanho() != 0 {
		t.Fatal("estado inicial inesperado")
	}
	a.Percorrer(func(string, int) bool { t.Fatal("não deveria visitar"); return true })
}

func TestRemoverTudoEmOrdens(t *testing.T) {
	for _, grau := range []int{2, 3, 4, 7} {
		for _, ordem := range []string{"crescente", "decrescente", "aleatoria"} {
			a, _ := Nova[int, int](grau)
			n := 400
			for i := 0; i < n; i++ {
				a.Inserir(i, i*10)
			}
			ks := rand.New(rand.NewSource(int64(grau))).Perm(n)
			switch ordem {
			case "crescente":
				sort.Ints(ks)
			case "decrescente":
				sort.Sort(sort.Reverse(sort.IntSlice(ks)))
			}
			for i, k := range ks {
				if !a.Remover(k) {
					t.Fatalf("t=%d %s: remover %d falhou", grau, ordem, k)
				}
				if a.Remover(k) {
					t.Fatalf("t=%d %s: remover %d duas vezes", grau, ordem, k)
				}
				if err := a.Validar(); err != nil {
					t.Fatalf("t=%d %s após %d remoções: %v", grau, ordem, i+1, err)
				}
			}
			if a.Tamanho() != 0 || a.Altura() != 1 {
				t.Fatalf("t=%d %s: árvore deveria estar vazia", grau, ordem)
			}
		}
	}
}

func TestContraMapaAleatorio(t *testing.T) {
	r := rand.New(rand.NewSource(42))
	a, _ := Nova[int, int](3)
	ref := map[int]int{}
	for i := 0; i < 20000; i++ {
		k := r.Intn(300)
		switch r.Intn(3) {
		case 0, 1:
			_, existia := ref[k]
			if novo := a.Inserir(k, i); novo == existia {
				t.Fatalf("inserir %d: novo=%v existia=%v", k, novo, existia)
			}
			ref[k] = i
		default:
			_, existia := ref[k]
			if a.Remover(k) != existia {
				t.Fatalf("remover %d inconsistente", k)
			}
			delete(ref, k)
		}
		if i%500 == 0 {
			if err := a.Validar(); err != nil {
				t.Fatalf("passo %d: %v", i, err)
			}
		}
	}
	if a.Tamanho() != len(ref) {
		t.Fatalf("tamanho %d != %d", a.Tamanho(), len(ref))
	}
	for k, v := range ref {
		if got, ok := a.Buscar(k); !ok || got != v {
			t.Fatalf("chave %d: (%d,%v) quer %d", k, got, ok, v)
		}
	}
}

func TestPercorrerInterrompe(t *testing.T) {
	a, _ := Nova[int, int](2)
	for i := 0; i < 100; i++ {
		a.Inserir(i, i)
	}
	var n int
	a.Percorrer(func(k, _ int) bool { n++; return k < 9 })
	if n != 10 {
		t.Fatalf("visitou %d, quer 10", n)
	}
}

func TestAlturaCresceLogaritmicamente(t *testing.T) {
	a, _ := Nova[int, int](16)
	for i := 0; i < 100000; i++ {
		a.Inserir(i, i)
	}
	if h := a.Altura(); h > 5 {
		t.Fatalf("altura %d alta demais", h)
	}
}
