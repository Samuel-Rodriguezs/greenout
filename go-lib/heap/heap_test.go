package heap

import (
	"math/rand"
	"slices"
	"testing"
)

func drenar[T any](h *Heap[T]) []T {
	r := []T{}
	for h.Tamanho() > 0 {
		v, _ := h.Extrair()
		r = append(r, v)
	}
	return r
}

func TestMinEMax(t *testing.T) {
	casos := []struct {
		nome  string
		antes func(a, b int) bool
		in    []int
		want  []int
	}{
		{"min", func(a, b int) bool { return a < b }, []int{5, 1, 4, 2, 3}, []int{1, 2, 3, 4, 5}},
		{"max", func(a, b int) bool { return a > b }, []int{5, 1, 4, 2, 3}, []int{5, 4, 3, 2, 1}},
		{"duplicados", func(a, b int) bool { return a < b }, []int{2, 2, 1, 1}, []int{1, 1, 2, 2}},
		{"vazio", func(a, b int) bool { return a < b }, nil, []int{}},
		{"um", func(a, b int) bool { return a < b }, []int{9}, []int{9}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			h := Novo(c.antes)
			for _, v := range c.in {
				h.Inserir(v)
			}
			if got := drenar(h); !slices.Equal(got, c.want) {
				t.Fatalf("got %v want %v", got, c.want)
			}
		})
	}
}

func TestVazio(t *testing.T) {
	h := Novo(func(a, b int) bool { return a < b })
	if _, ok := h.Topo(); ok {
		t.Fatal("topo vazio")
	}
	if _, ok := h.Extrair(); ok {
		t.Fatal("extrair vazio")
	}
	h.Inserir(3)
	h.Inserir(1)
	if v, _ := h.Topo(); v != 1 || h.Tamanho() != 2 {
		t.Fatal("topo não deve remover")
	}
}

func TestComparadorDeStruct(t *testing.T) {
	type tarefa struct {
		nome string
		prio int
	}
	h := Novo(func(a, b tarefa) bool { return a.prio > b.prio })
	h.Inserir(tarefa{"baixa", 1})
	h.Inserir(tarefa{"alta", 9})
	h.Inserir(tarefa{"media", 5})
	got := []string{}
	for _, v := range drenar(h) {
		got = append(got, v.nome)
	}
	if !slices.Equal(got, []string{"alta", "media", "baixa"}) {
		t.Fatalf("got %v", got)
	}
}

func TestAleatorio(t *testing.T) {
	r := rand.New(rand.NewSource(42))
	in := make([]int, 500)
	h := Novo(func(a, b int) bool { return a < b })
	for i := range in {
		in[i] = r.Intn(100)
		h.Inserir(in[i])
	}
	slices.Sort(in)
	if got := drenar(h); !slices.Equal(got, in) {
		t.Fatal("heap não produziu ordem crescente")
	}
}
