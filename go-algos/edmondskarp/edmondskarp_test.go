package edmondskarp

import "testing"

func TestFluxoMaximo(t *testing.T) {
	casos := []struct {
		nome    string
		n       int
		arestas []Aresta
		s, t    int
		want    int
	}{
		{"CLRS", 6, []Aresta{{0, 1, 16}, {0, 2, 13}, {1, 2, 10}, {2, 1, 4}, {1, 3, 12}, {3, 2, 9}, {2, 4, 14}, {4, 3, 7}, {3, 5, 20}, {4, 5, 4}}, 0, 5, 23},
		{"caminho simples gargalo", 3, []Aresta{{0, 1, 5}, {1, 2, 3}}, 0, 2, 3},
		{"sem caminho", 3, []Aresta{{0, 1, 5}}, 0, 2, 0},
		{"origem igual destino", 2, []Aresta{{0, 1, 5}}, 0, 0, 0},
		{"paralelas", 2, []Aresta{{0, 1, 2}, {0, 1, 3}}, 0, 1, 5},
		{"diamante", 4, []Aresta{{0, 1, 10}, {0, 2, 10}, {1, 3, 4}, {2, 3, 9}, {1, 2, 6}}, 0, 3, 13},
		{"índice inválido", 2, nil, 0, 5, 0},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := FluxoMaximo(c.n, c.arestas, c.s, c.t); got != c.want {
				t.Errorf("fluxo=%d, esperado %d", got, c.want)
			}
		})
	}
}
