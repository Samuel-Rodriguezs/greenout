package troco

import (
	"reflect"
	"testing"
)

func TestMinimo(t *testing.T) {
	casos := []struct {
		nome   string
		moedas []int
		valor  int
		qtd    int
		usadas []int
	}{
		{"canônico", []int{1, 5, 10, 25}, 63, 6, []int{1, 1, 1, 10, 25, 25}},
		{"guloso falha", []int{1, 3, 4}, 6, 2, []int{3, 3}},
		{"impossível", []int{2}, 3, -1, nil},
		{"valor zero", []int{1, 2}, 0, 0, nil},
		{"sem moedas", nil, 5, -1, nil},
		{"valor negativo", []int{1}, -1, -1, nil},
		{"leetcode 11", []int{1, 2, 5}, 11, 3, []int{1, 5, 5}},
		{"moeda inválida ignorada", []int{0, -1, 3}, 9, 3, []int{3, 3, 3}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			qtd, usadas := Minimo(c.moedas, c.valor)
			if qtd != c.qtd || !reflect.DeepEqual(usadas, c.usadas) {
				t.Errorf("qtd=%d usadas=%v", qtd, usadas)
			}
		})
	}
}

func TestFormas(t *testing.T) {
	casos := []struct {
		moedas []int
		valor  int
		want   int
	}{
		{[]int{1, 2, 5}, 5, 4},
		{[]int{2}, 3, 0},
		{[]int{1, 2, 3}, 4, 4},
		{nil, 0, 1},
		{[]int{7}, 0, 1},
		{[]int{1}, -3, 0},
	}
	for _, c := range casos {
		if got := Formas(c.moedas, c.valor); got != c.want {
			t.Errorf("Formas(%v,%d)=%d, esperado %d", c.moedas, c.valor, got, c.want)
		}
	}
}
