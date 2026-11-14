package lab

import (
	"errors"
	"testing"
)

func TestRPNAvaliar(t *testing.T) {
	casos := []struct {
		nome string
		expr string
		want float64
		err  error
	}{
		{"numero", "42", 42, nil},
		{"soma", "3 4 +", 7, nil},
		{"subtracao ordem", "10 4 -", 6, nil},
		{"divisao", "9 2 /", 4.5, nil},
		{"composta", "5 1 2 + 4 * + 3 -", 14, nil},
		{"decimais", "1.5 2.5 +", 4, nil},
		{"negativo", "-3 2 *", -6, nil},
		{"espacos extras", "  2   3  * ", 6, nil},
		{"vazia", "   ", 0, ErrRPNVazia},
		{"operandos insuficientes", "1 +", 0, ErrRPNOperandos},
		{"operador sozinho", "*", 0, ErrRPNOperandos},
		{"sobra", "1 2", 0, ErrRPNSobra},
		{"divisao por zero", "1 0 /", 0, ErrRPNDivisaoZero},
		{"token invalido", "1 x +", 0, ErrRPNTokenInvalid},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			got, err := RPNAvaliar(c.expr)
			if !errors.Is(err, c.err) {
				t.Fatalf("err = %v, esperado %v", err, c.err)
			}
			if got != c.want {
				t.Fatalf("got %v want %v", got, c.want)
			}
		})
	}
}
