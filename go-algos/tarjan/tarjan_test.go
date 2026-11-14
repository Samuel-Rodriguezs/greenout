package tarjan

import (
	"reflect"
	"sort"
	"testing"
)

func normaliza(comps [][]int) [][]int {
	for _, c := range comps {
		sort.Ints(c)
	}
	sort.Slice(comps, func(i, j int) bool { return comps[i][0] < comps[j][0] })
	return comps
}

func TestSCC(t *testing.T) {
	casos := []struct {
		nome string
		adj  [][]int
		want [][]int
	}{
		{"três componentes", [][]int{{1}, {2}, {0, 3}, {4}, {5}, {3}}, [][]int{{0, 1, 2}, {3, 4, 5}}},
		{"dag", [][]int{{1}, {2}, {}}, [][]int{{0}, {1}, {2}}},
		{"ciclo único", [][]int{{1}, {2}, {0}}, [][]int{{0, 1, 2}}},
		{"clássico wikipedia", [][]int{{1}, {2}, {0}, {1, 2, 4}, {3, 5}, {2, 6}, {5}, {4, 6, 7}},
			[][]int{{0, 1, 2}, {3, 4}, {5, 6}, {7}}},
		{"vazio", [][]int{}, nil},
		{"laço", [][]int{{0}}, [][]int{{0}}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			got := normaliza(SCC(c.adj))
			if !reflect.DeepEqual(got, c.want) {
				t.Errorf("got %v, esperado %v", got, c.want)
			}
		})
	}
}

func TestOrdemSumidourosPrimeiro(t *testing.T) {
	// 0 -> 1: o componente {1} deve sair antes de {0}.
	comps := SCC([][]int{{1}, {}})
	if len(comps) != 2 || comps[0][0] != 1 {
		t.Errorf("ordem inesperada: %v", comps)
	}
}
