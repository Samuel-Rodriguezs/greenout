package lab

import "errors"

// ErrFibonacciInvalido indica n negativo ou que estoura uint64 (n > 93).
var ErrFibonacciInvalido = errors.New("fibonacci: n fora do intervalo 0..93")

// FibonacciMemo calcula o n-ésimo Fibonacci usando memoização.
func FibonacciMemo(n int) (uint64, error) {
	if n < 0 || n > 93 {
		return 0, ErrFibonacciInvalido
	}
	memo := make(map[int]uint64)
	var f func(int) uint64
	f = func(k int) uint64 {
		if k < 2 {
			return uint64(k)
		}
		if v, ok := memo[k]; ok {
			return v
		}
		v := f(k-1) + f(k-2)
		memo[k] = v
		return v
	}
	return f(n), nil
}
