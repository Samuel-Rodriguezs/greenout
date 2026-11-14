package kruskal

import "testing"

func TestAGM(t *testing.T) {
	casos := []struct {
		nome    string
		n       int
		arestas []Aresta
		total   int
		qtd     int
		ok      bool
	}{
		{"clássico", 5, []Aresta{{0, 1, 2}, {0, 3, 6}, {1, 2, 3}, {1, 3, 8}, {1, 4, 5}, {2, 4, 7}, {3, 4, 9}}, 16, 4, true},
		{"desconexo", 4, []Aresta{{0, 1, 1}, {2, 3, 4}}, 5, 2, false},
		{"vértice único", 1, nil, 0, 0, true},
		{"vazio", 0, nil, 0, 0, true},
		{"arestas paralelas e laço", 2, []Aresta{{0, 1, 9}, {0, 1, 2}, {1, 1, 1}}, 2, 1, true},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			total, esc, ok := AGM(c.n, c.arestas)
			if total != c.total || len(esc) != c.qtd || ok != c.ok {
				t.Errorf("total=%d qtd=%d ok=%v", total, len(esc), ok)
			}
		})
	}
}
