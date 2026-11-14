package prim

import "testing"

func nao(n int, arestas [][3]int) [][]Aresta {
	g := make([][]Aresta, n)
	for _, e := range arestas {
		g[e[0]] = append(g[e[0]], Aresta{e[1], e[2]})
		g[e[1]] = append(g[e[1]], Aresta{e[0], e[2]})
	}
	return g
}

func TestAGM(t *testing.T) {
	casos := []struct {
		nome  string
		g     [][]Aresta
		total int
		ok    bool
	}{
		{"clássico", nao(5, [][3]int{{0, 1, 2}, {0, 3, 6}, {1, 2, 3}, {1, 3, 8}, {1, 4, 5}, {2, 4, 7}, {3, 4, 9}}), 16, true},
		{"desconexo", nao(4, [][3]int{{0, 1, 1}, {2, 3, 4}}), 1, false},
		{"único", nao(1, nil), 0, true},
		{"vazio", nil, 0, true},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			total, pai, ok := AGM(c.g)
			if total != c.total || ok != c.ok || len(pai) != len(c.g) {
				t.Errorf("total=%d ok=%v pai=%v", total, ok, pai)
			}
		})
	}
}
