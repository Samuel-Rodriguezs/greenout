package lab

import (
	"reflect"
	"testing"
)

func TestCrivoPrimos(t *testing.T) {
	casos := []struct {
		nome   string
		limite int
		want   []int
	}{
		{"negativo", -5, []int{}},
		{"zero", 0, []int{}},
		{"um", 1, []int{}},
		{"dois", 2, []int{2}},
		{"dez", 10, []int{2, 3, 5, 7}},
		{"limite primo", 13, []int{2, 3, 5, 7, 11, 13}},
		{"trinta", 30, []int{2, 3, 5, 7, 11, 13, 17, 19, 23, 29}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := CrivoPrimos(c.limite); !reflect.DeepEqual(got, c.want) {
				t.Fatalf("got %v, want %v", got, c.want)
			}
		})
	}
	if n := len(CrivoPrimos(1000)); n != 168 {
		t.Fatalf("esperados 168 primos até 1000, got %d", n)
	}
}
