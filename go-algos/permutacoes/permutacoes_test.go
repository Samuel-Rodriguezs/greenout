package permutacoes

import (
	"reflect"
	"testing"
)

func TestPermutacoes(t *testing.T) {
	casos := []struct {
		nome string
		v    []int
		want [][]int
	}{
		{"três", []int{3, 1, 2}, [][]int{{1, 2, 3}, {1, 3, 2}, {2, 1, 3}, {2, 3, 1}, {3, 1, 2}, {3, 2, 1}}},
		{"repetidos", []int{1, 1, 2}, [][]int{{1, 1, 2}, {1, 2, 1}, {2, 1, 1}}},
		{"único", []int{5}, [][]int{{5}}},
		{"vazio", nil, [][]int{{}}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := Permutacoes(c.v); !reflect.DeepEqual(got, c.want) {
				t.Errorf("got %v, esperado %v", got, c.want)
			}
		})
	}
}

func TestContagemPermutacoes(t *testing.T) {
	fat := []int{1, 1, 2, 6, 24, 120, 720, 5040}
	for n := 0; n < len(fat); n++ {
		v := make([]int, n)
		for i := range v {
			v[i] = i
		}
		if got := len(Permutacoes(v)); got != fat[n] {
			t.Errorf("n=%d: %d permutações, esperado %d", n, got, fat[n])
		}
	}
}

func TestEntradaNaoAlterada(t *testing.T) {
	v := []int{3, 1, 2}
	Permutacoes(v)
	if !reflect.DeepEqual(v, []int{3, 1, 2}) {
		t.Errorf("entrada alterada: %v", v)
	}
}

func TestCombinacoes(t *testing.T) {
	casos := []struct {
		nome string
		n, k int
		want [][]int
	}{
		{"4 escolhe 2", 4, 2, [][]int{{1, 2}, {1, 3}, {1, 4}, {2, 3}, {2, 4}, {3, 4}}},
		{"k zero", 3, 0, [][]int{{}}},
		{"k igual n", 3, 3, [][]int{{1, 2, 3}}},
		{"k maior que n", 2, 3, nil},
		{"k negativo", 3, -1, nil},
		{"n zero k zero", 0, 0, [][]int{{}}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := Combinacoes(c.n, c.k); !reflect.DeepEqual(got, c.want) {
				t.Errorf("got %v, esperado %v", got, c.want)
			}
		})
	}
	if got := len(Combinacoes(10, 4)); got != 210 {
		t.Errorf("C(10,4)=%d, esperado 210", got)
	}
}
