package lab

import (
	"reflect"
	"testing"
)

func TestFizzBuzzLista(t *testing.T) {
	casos := []struct {
		nome string
		n    int
		want []string
		err  error
	}{
		{"um", 1, []string{"1"}, nil},
		{"cinco", 5, []string{"1", "2", "Fizz", "4", "Buzz"}, nil},
		{"zero", 0, nil, ErrFizzBuzzLimiteInvalido},
		{"negativo", -3, nil, ErrFizzBuzzLimiteInvalido},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			got, err := FizzBuzzLista(c.n)
			if err != c.err {
				t.Fatalf("erro = %v, esperado %v", err, c.err)
			}
			if !reflect.DeepEqual(got, c.want) {
				t.Fatalf("got %v, want %v", got, c.want)
			}
		})
	}
}

func TestFizzBuzzListaQuinze(t *testing.T) {
	got, err := FizzBuzzLista(15)
	if err != nil || len(got) != 15 {
		t.Fatalf("got %v, %v", got, err)
	}
	if got[14] != "FizzBuzz" || got[2] != "Fizz" || got[9] != "Buzz" || got[0] != "1" {
		t.Fatalf("saida inesperada: %v", got)
	}
}
