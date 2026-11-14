package calculadora

import (
	"errors"
	"math"
	"testing"
)

func TestAvaliar(t *testing.T) {
	casos := []struct {
		expr string
		want float64
	}{
		{"1 + 2", 3},
		{"2 + 3 * 4", 14},
		{"(2 + 3) * 4", 20},
		{"10 / 4", 2.5},
		{"2 ^ 3 ^ 2", 512},
		{"-3 + 5", 2},
		{"--4", 4},
		{"-(2 + 3)", -5},
		{"1.5 * 2", 3},
		{"10 - 2 - 3", 5},
		{"2 * -3", -6},
	}
	for _, c := range casos {
		t.Run(c.expr, func(t *testing.T) {
			got, err := Avaliar(c.expr)
			if err != nil {
				t.Fatal(err)
			}
			if math.Abs(got-c.want) > 1e-9 {
				t.Errorf("got %v, want %v", got, c.want)
			}
		})
	}
}

func TestAvaliarErros(t *testing.T) {
	casos := []struct {
		expr string
		err  error
	}{
		{"1 / 0", ErrDivisaoPorZero},
		{"(1 + 2", ErrSintaxe},
		{"1 + ", ErrSintaxe},
		{"1 2", ErrSintaxe},
		{"abc", ErrSintaxe},
		{"1..2 + 1", ErrSintaxe},
		{"", ErrSintaxe},
		{")", ErrSintaxe},
	}
	for _, c := range casos {
		t.Run(c.expr, func(t *testing.T) {
			_, err := Avaliar(c.expr)
			if !errors.Is(err, c.err) {
				t.Errorf("erro = %v, esperado %v", err, c.err)
			}
		})
	}
}
