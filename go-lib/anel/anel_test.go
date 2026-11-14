package anel

import (
	"slices"
	"testing"
)

func TestEscreverLer(t *testing.T) {
	casos := []struct {
		nome   string
		cap    int
		escr   []int
		itens  []int
		sobres int
	}{
		{"abaixo da capacidade", 3, []int{1, 2}, []int{1, 2}, 0},
		{"exato", 3, []int{1, 2, 3}, []int{1, 2, 3}, 0},
		{"sobrescreve", 3, []int{1, 2, 3, 4, 5}, []int{3, 4, 5}, 2},
		{"capacidade 1", 1, []int{1, 2, 3}, []int{3}, 2},
		{"capacidade invalida", 0, []int{7, 8}, []int{8}, 1},
		{"vazio", 2, nil, []int{}, 0},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			a := Novo[int](c.cap)
			n := 0
			for _, v := range c.escr {
				if a.Escrever(v) {
					n++
				}
			}
			if n != c.sobres {
				t.Fatalf("sobrescritas %d", n)
			}
			if got := a.Itens(); !slices.Equal(got, c.itens) {
				t.Fatalf("itens %v", got)
			}
			for _, want := range c.itens {
				if v, ok := a.Ler(); !ok || v != want {
					t.Fatalf("ler %d want %d", v, want)
				}
			}
			if _, ok := a.Ler(); ok {
				t.Fatal("deveria estar vazio")
			}
		})
	}
}

func TestCheioECapacidade(t *testing.T) {
	a := Novo[string](2)
	if a.Cheio() || a.Capacidade() != 2 {
		t.Fatal("estado inicial")
	}
	a.Escrever("a")
	a.Escrever("b")
	if !a.Cheio() || a.Tamanho() != 2 {
		t.Fatal("deveria estar cheio")
	}
	a.Ler()
	a.Escrever("c") // dá a volta no buffer
	if got := a.Itens(); !slices.Equal(got, []string{"b", "c"}) {
		t.Fatalf("got %v", got)
	}
}
