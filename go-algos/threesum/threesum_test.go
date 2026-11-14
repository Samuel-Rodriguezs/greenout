package threesum

import (
	"reflect"
	"testing"
)

func TestSomaZero(t *testing.T) {
	casos := []struct {
		nome string
		nums []int
		want [][3]int
	}{
		{"clássico", []int{-1, 0, 1, 2, -1, -4}, [][3]int{{-1, -1, 2}, {-1, 0, 1}}},
		{"nenhuma", []int{1, 2, 3}, nil},
		{"zeros", []int{0, 0, 0, 0}, [][3]int{{0, 0, 0}}},
		{"poucos elementos", []int{0, 0}, nil},
		{"vazio", nil, nil},
		{"duplicatas", []int{-2, 0, 0, 2, 2}, [][3]int{{-2, 0, 2}}},
		{"muitas", []int{-4, -2, -2, -2, 0, 1, 2, 2, 2, 3, 3, 4, 4, 6, 6}, [][3]int{
			{-4, -2, 6}, {-4, 0, 4}, {-4, 1, 3}, {-4, 2, 2}, {-2, -2, 4}, {-2, 0, 2},
		}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := SomaZero(c.nums); !reflect.DeepEqual(got, c.want) {
				t.Errorf("got %v, esperado %v", got, c.want)
			}
		})
	}
}

func TestAlvo(t *testing.T) {
	got := Trincas([]int{1, 2, 3, 4, 5}, 9)
	want := [][3]int{{1, 3, 5}, {2, 3, 4}}
	if !reflect.DeepEqual(got, want) {
		t.Errorf("got %v, esperado %v", got, want)
	}
}

func TestEntradaNaoAlterada(t *testing.T) {
	v := []int{3, -1, 2, -2}
	Trincas(v, 0)
	if !reflect.DeepEqual(v, []int{3, -1, 2, -2}) {
		t.Errorf("entrada alterada: %v", v)
	}
}
