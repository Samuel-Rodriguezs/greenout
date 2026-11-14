package janelamax

import (
	"math/rand"
	"reflect"
	"testing"
)

func TestMaximos(t *testing.T) {
	casos := []struct {
		nome string
		a    []int
		k    int
		want []int
	}{
		{"clássico", []int{1, 3, -1, -3, 5, 3, 6, 7}, 3, []int{3, 3, 5, 5, 6, 7}},
		{"k um", []int{4, 2, 9}, 1, []int{4, 2, 9}},
		{"k igual ao tamanho", []int{4, 2, 9}, 3, []int{9}},
		{"k maior", []int{1}, 2, nil},
		{"k zero", []int{1}, 0, nil},
		{"vazio", nil, 1, nil},
		{"iguais", []int{2, 2, 2, 2}, 2, []int{2, 2, 2}},
		{"decrescente", []int{5, 4, 3, 2, 1}, 2, []int{5, 4, 3, 2}},
		{"crescente", []int{1, 2, 3, 4, 5}, 2, []int{2, 3, 4, 5}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := Maximos(c.a, c.k); !reflect.DeepEqual(got, c.want) {
				t.Errorf("got %v, esperado %v", got, c.want)
			}
		})
	}
}

func TestAleatorio(t *testing.T) {
	r := rand.New(rand.NewSource(8))
	for it := 0; it < 200; it++ {
		a := make([]int, 1+r.Intn(30))
		for i := range a {
			a[i] = r.Intn(10)
		}
		k := 1 + r.Intn(len(a))
		var want []int
		for i := 0; i+k <= len(a); i++ {
			want = append(want, slicesMax(a[i:i+k]))
		}
		if got := Maximos(a, k); !reflect.DeepEqual(got, want) {
			t.Fatalf("a=%v k=%d got %v, esperado %v", a, k, got, want)
		}
	}
}

func slicesMax(s []int) int {
	m := s[0]
	for _, x := range s {
		m = max(m, x)
	}
	return m
}
