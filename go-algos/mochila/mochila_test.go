package mochila

import (
	"reflect"
	"testing"
)

func TestZero1(t *testing.T) {
	casos := []struct {
		nome    string
		pesos   []int
		valores []int
		cap     int
		valor   int
		itens   []int
	}{
		{"clássico", []int{1, 3, 4, 5}, []int{1, 4, 5, 7}, 7, 9, []int{1, 2}},
		{"capacidade zero", []int{1, 2}, []int{10, 20}, 0, 0, nil},
		{"nenhum cabe", []int{5, 6}, []int{10, 20}, 4, 0, nil},
		{"sem itens", nil, nil, 10, 0, nil},
		{"todos cabem", []int{1, 2, 3}, []int{6, 10, 12}, 6, 28, []int{0, 1, 2}},
		{"60-100-120", []int{10, 20, 30}, []int{60, 100, 120}, 50, 220, []int{1, 2}},
		{"capacidade negativa", []int{1}, []int{1}, -1, 0, nil},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			v, it := Zero1(c.pesos, c.valores, c.cap)
			if v != c.valor || !reflect.DeepEqual(it, c.itens) {
				t.Errorf("valor=%d itens=%v", v, it)
			}
		})
	}
}

func TestIlimitada(t *testing.T) {
	casos := []struct {
		nome    string
		pesos   []int
		valores []int
		cap     int
		want    int
	}{
		{"repete item", []int{1, 3, 4, 5}, []int{10, 40, 50, 70}, 8, 110},
		{"capacidade zero", []int{2}, []int{3}, 0, 0},
		{"item único repetido", []int{2}, []int{3}, 9, 12},
		{"nenhum cabe", []int{10}, []int{5}, 3, 0},
		{"peso zero ignorado", []int{0, 2}, []int{100, 3}, 4, 6},
		{"vazio", nil, nil, 5, 0},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := Ilimitada(c.pesos, c.valores, c.cap); got != c.want {
				t.Errorf("got %d, esperado %d", got, c.want)
			}
		})
	}
}
