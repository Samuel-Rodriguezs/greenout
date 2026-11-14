package matrizcadeia

import "testing"

func TestMinimo(t *testing.T) {
	casos := []struct {
		nome  string
		dims  []int
		custo int
		par   string
	}{
		{"CLRS", []int{30, 35, 15, 5, 10, 20, 25}, 15125, "((A1 x (A2 x A3)) x ((A4 x A5) x A6))"},
		{"três matrizes", []int{10, 30, 5, 60}, 4500, "((A1 x A2) x A3)"},
		{"quatro matrizes", []int{40, 20, 30, 10, 30}, 26000, "((A1 x (A2 x A3)) x A4)"},
		{"uma matriz", []int{4, 5}, 0, "A1"},
		{"duas matrizes", []int{2, 3, 4}, 24, "(A1 x A2)"},
		{"sem matrizes", []int{5}, 0, ""},
		{"vazio", nil, 0, ""},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			custo, par := Minimo(c.dims)
			if custo != c.custo || par != c.par {
				t.Errorf("custo=%d par=%q", custo, par)
			}
		})
	}
}
