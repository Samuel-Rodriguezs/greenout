package conjunto

import (
	"slices"
	"testing"
)

func ordenado(c *Conjunto[int]) []int {
	r := c.Itens()
	slices.Sort(r)
	return r
}

func TestAdicionarRemoverContem(t *testing.T) {
	c := Novo(1, 2, 2)
	if c.Tamanho() != 2 {
		t.Fatalf("tamanho %d", c.Tamanho())
	}
	if c.Adicionar(1) || !c.Adicionar(3) {
		t.Fatal("Adicionar retornou valor errado")
	}
	if !c.Contem(3) || c.Contem(9) {
		t.Fatal("Contem errado")
	}
	if !c.Remover(3) || c.Remover(3) {
		t.Fatal("Remover retornou valor errado")
	}
	if Novo[int]().Tamanho() != 0 {
		t.Fatal("vazio")
	}
}

func TestOperacoes(t *testing.T) {
	casos := []struct {
		nome       string
		a, b       []int
		uni, inter []int
		dif        []int
	}{
		{"parcial", []int{1, 2, 3}, []int{2, 3, 4}, []int{1, 2, 3, 4}, []int{2, 3}, []int{1}},
		{"disjuntos", []int{1}, []int{2}, []int{1, 2}, []int{}, []int{1}},
		{"vazio", nil, []int{1}, []int{1}, []int{}, []int{}},
		{"iguais", []int{5}, []int{5}, []int{5}, []int{5}, []int{}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			a, b := Novo(c.a...), Novo(c.b...)
			if got := ordenado(a.Uniao(b)); !slices.Equal(got, c.uni) {
				t.Fatalf("uniao %v", got)
			}
			if got := ordenado(a.Intersecao(b)); !slices.Equal(got, c.inter) {
				t.Fatalf("inter %v", got)
			}
			if got := ordenado(a.Diferenca(b)); !slices.Equal(got, c.dif) {
				t.Fatalf("dif %v", got)
			}
		})
	}
}

func TestIgual(t *testing.T) {
	if !Novo(1, 2).Igual(Novo(2, 1)) {
		t.Fatal("deveriam ser iguais")
	}
	if Novo(1, 2).Igual(Novo(1, 3)) || Novo(1).Igual(Novo(1, 2)) {
		t.Fatal("deveriam diferir")
	}
}
