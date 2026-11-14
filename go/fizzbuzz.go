package lab

import (
	"errors"
	"strconv"
)

// ErrFizzBuzzLimiteInvalido indica que o limite informado é menor que 1.
var ErrFizzBuzzLimiteInvalido = errors.New("fizzbuzz: limite deve ser >= 1")

// FizzBuzzLista devolve os textos do FizzBuzz de 1 até n.
func FizzBuzzLista(n int) ([]string, error) {
	if n < 1 {
		return nil, ErrFizzBuzzLimiteInvalido
	}
	saida := make([]string, 0, n)
	for i := 1; i <= n; i++ {
		switch {
		case i%15 == 0:
			saida = append(saida, "FizzBuzz")
		case i%3 == 0:
			saida = append(saida, "Fizz")
		case i%5 == 0:
			saida = append(saida, "Buzz")
		default:
			saida = append(saida, strconv.Itoa(i))
		}
	}
	return saida, nil
}
