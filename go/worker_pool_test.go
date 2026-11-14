package lab

import (
	"reflect"
	"sync/atomic"
	"testing"
)

func TestPoolExecutar(t *testing.T) {
	quadrado := func(x int) int { return x * x }
	casos := []struct {
		nome    string
		entrada []int
		n       int
		want    []int
	}{
		{"vazio", []int{}, 3, []int{}},
		{"um trabalhador", []int{1, 2, 3}, 1, []int{1, 4, 9}},
		{"mais trabalhadores que tarefas", []int{2, 3}, 8, []int{4, 9}},
		{"varios", []int{1, 2, 3, 4, 5, 6, 7, 8, 9, 10}, 4, []int{1, 4, 9, 16, 25, 36, 49, 64, 81, 100}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			got, err := PoolExecutar(c.entrada, c.n, quadrado)
			if err != nil || !reflect.DeepEqual(got, c.want) {
				t.Fatalf("got %v, %v", got, err)
			}
		})
	}
}

func TestPoolExecutarInvalido(t *testing.T) {
	for _, n := range []int{0, -1} {
		if _, err := PoolExecutar([]int{1}, n, func(x int) int { return x }); err != ErrPoolTrabalhadoresInvalido {
			t.Fatalf("n=%d err=%v", n, err)
		}
	}
}

func TestPoolExecutarChamaUmaVezCada(t *testing.T) {
	var chamadas atomic.Int64
	entrada := make([]int, 500)
	for i := range entrada {
		entrada[i] = i
	}
	got, err := PoolExecutar(entrada, 7, func(x int) string {
		chamadas.Add(1)
		return string(rune('a' + x%26))
	})
	if err != nil || len(got) != 500 || chamadas.Load() != 500 {
		t.Fatalf("len=%d chamadas=%d err=%v", len(got), chamadas.Load(), err)
	}
	if got[27] != "b" {
		t.Fatalf("got[27] = %q", got[27])
	}
}
