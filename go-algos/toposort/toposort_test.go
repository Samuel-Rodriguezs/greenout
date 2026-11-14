package toposort

import "testing"

func valida(t *testing.T, adj [][]int, ordem []int) {
	t.Helper()
	if len(ordem) != len(adj) {
		t.Fatalf("ordem %v com tamanho errado", ordem)
	}
	posicao := make(map[int]int)
	for i, v := range ordem {
		posicao[v] = i
	}
	if len(posicao) != len(adj) {
		t.Fatalf("ordem %v tem repetidos", ordem)
	}
	for u, vs := range adj {
		for _, v := range vs {
			if posicao[u] >= posicao[v] {
				t.Errorf("aresta %d->%d violada em %v", u, v, ordem)
			}
		}
	}
}

func TestOrdenacao(t *testing.T) {
	casos := []struct {
		nome string
		adj  [][]int
		ok   bool
	}{
		{"dag clássico", [][]int{{1, 2}, {3}, {3}, {4}, {}}, true},
		{"vestir roupas", [][]int{{1}, {}, {3, 4}, {4}, {}, {6}, {}}, true},
		{"sem arestas", [][]int{{}, {}, {}}, true},
		{"vazio", [][]int{}, true},
		{"ciclo", [][]int{{1}, {2}, {0}}, false},
		{"laço", [][]int{{0}}, false},
		{"ciclo em componente", [][]int{{}, {2}, {1}}, false},
	}
	algos := map[string]func([][]int) ([]int, bool){"Kahn": Kahn, "DFS": DFS}
	for nome, f := range algos {
		for _, c := range casos {
			t.Run(nome+"/"+c.nome, func(t *testing.T) {
				ordem, ok := f(c.adj)
				if ok != c.ok {
					t.Fatalf("ok=%v, esperado %v", ok, c.ok)
				}
				if ok {
					valida(t, c.adj, ordem)
				}
			})
		}
	}
}
