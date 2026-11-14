package lab

import (
	"errors"
	"fmt"
	"strconv"
	"strings"
)

// Erros do avaliador RPN.
var (
	ErrRPNVazia        = errors.New("rpn: expressão vazia")
	ErrRPNOperandos    = errors.New("rpn: operandos insuficientes")
	ErrRPNSobra        = errors.New("rpn: operandos em excesso")
	ErrRPNDivisaoZero  = errors.New("rpn: divisão por zero")
	ErrRPNTokenInvalid = errors.New("rpn: token inválido")
)

// RPNAvaliar avalia uma expressão em notação polonesa reversa, com tokens
// separados por espaço e operadores + - * /.
func RPNAvaliar(expr string) (float64, error) {
	tokens := strings.Fields(expr)
	if len(tokens) == 0 {
		return 0, ErrRPNVazia
	}
	var pilha []float64
	for _, tk := range tokens {
		switch tk {
		case "+", "-", "*", "/":
			if len(pilha) < 2 {
				return 0, ErrRPNOperandos
			}
			a, b := pilha[len(pilha)-2], pilha[len(pilha)-1]
			pilha = pilha[:len(pilha)-2]
			var r float64
			switch tk {
			case "+":
				r = a + b
			case "-":
				r = a - b
			case "*":
				r = a * b
			case "/":
				if b == 0 {
					return 0, ErrRPNDivisaoZero
				}
				r = a / b
			}
			pilha = append(pilha, r)
		default:
			v, err := strconv.ParseFloat(tk, 64)
			if err != nil {
				return 0, fmt.Errorf("%w: %q", ErrRPNTokenInvalid, tk)
			}
			pilha = append(pilha, v)
		}
	}
	if len(pilha) != 1 {
		return 0, ErrRPNSobra
	}
	return pilha[0], nil
}
