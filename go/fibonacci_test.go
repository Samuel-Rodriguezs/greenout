package lab

import "testing"

func TestFibonacciMemo(t *testing.T) {
	casos := []struct {
		n    int
		want uint64
		err  error
	}{
		{0, 0, nil},
		{1, 1, nil},
		{2, 1, nil},
		{10, 55, nil},
		{50, 12586269025, nil},
		{93, 12200160415121876738, nil},
		{94, 0, ErrFibonacciInvalido},
		{-1, 0, ErrFibonacciInvalido},
	}
	for _, c := range casos {
		got, err := FibonacciMemo(c.n)
		if err != c.err || got != c.want {
			t.Errorf("FibonacciMemo(%d) = %d, %v", c.n, got, err)
		}
	}
}
