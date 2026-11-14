package floydwarshall

import (
	"reflect"
	"testing"
)

func TestTodosPares(t *testing.T) {
	casos := []struct {
		nome string
		m    [][]int
		d    [][]int
		neg  bool
	}{
		{"clássico", [][]int{{0, 3, Inf, 7}, {8, 0, 2, Inf}, {5, Inf, 0, 1}, {2, Inf, Inf, 0}},
			[][]int{{0, 3, 5, 6}, {5, 0, 2, 3}, {3, 6, 0, 1}, {2, 5, 7, 0}}, false},
		{"desconexo", [][]int{{0, Inf}, {Inf, 0}}, [][]int{{0, Inf}, {Inf, 0}}, false},
		{"negativo sem ciclo", [][]int{{0, -2}, {Inf, 0}}, [][]int{{0, -2}, {Inf, 0}}, false},
		{"vazio", [][]int{}, [][]int{}, false},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			d, neg := TodosPares(c.m)
			if neg != c.neg || !reflect.DeepEqual(d, c.d) {
				t.Errorf("d=%v neg=%v", d, neg)
			}
		})
	}
}

func TestCicloNegativo(t *testing.T) {
	_, neg := TodosPares([][]int{{0, 1, Inf}, {Inf, 0, -3}, {1, Inf, 0}})
	if !neg {
		t.Error("deveria detectar ciclo negativo")
	}
}
