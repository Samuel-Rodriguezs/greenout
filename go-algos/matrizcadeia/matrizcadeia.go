// Pacote matrizcadeia resolve a multiplicação de cadeia de matrizes.
package matrizcadeia

import "strconv"

// Minimo recebe as dimensões (a matriz i tem dims[i] x dims[i+1]) e devolve o
// menor número de multiplicações escalares e a parentetização ótima.
func Minimo(dims []int) (int, string) {
	n := len(dims) - 1 // quantidade de matrizes
	if n <= 0 {
		return 0, ""
	}
	custo := make([][]int, n)
	corte := make([][]int, n)
	for i := range custo {
		custo[i] = make([]int, n)
		corte[i] = make([]int, n)
	}
	for tam := 2; tam <= n; tam++ {
		for i := 0; i+tam-1 < n; i++ {
			j := i + tam - 1
			custo[i][j] = int(^uint(0) >> 1)
			for k := i; k < j; k++ {
				c := custo[i][k] + custo[k+1][j] + dims[i]*dims[k+1]*dims[j+1]
				if c < custo[i][j] {
					custo[i][j] = c
					corte[i][j] = k
				}
			}
		}
	}
	var monta func(i, j int) string
	monta = func(i, j int) string {
		if i == j {
			return "A" + strconv.Itoa(i+1)
		}
		return "(" + monta(i, corte[i][j]) + " x " + monta(corte[i][j]+1, j) + ")"
	}
	return custo[0][n-1], monta(0, n-1)
}
