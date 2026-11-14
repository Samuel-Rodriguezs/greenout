// Pacote janelamax calcula o máximo de cada janela deslizante com deque monotônico.
package janelamax

// Maximos devolve o máximo de cada janela de tamanho k de a, em O(n).
// Devolve nil se k <= 0 ou k > len(a).
func Maximos(a []int, k int) []int {
	if k <= 0 || k > len(a) {
		return nil
	}
	res := make([]int, 0, len(a)-k+1)
	var dq []int // índices com valores em ordem decrescente
	for i, x := range a {
		for len(dq) > 0 && a[dq[len(dq)-1]] <= x {
			dq = dq[:len(dq)-1]
		}
		dq = append(dq, i)
		if dq[0] <= i-k {
			dq = dq[1:]
		}
		if i >= k-1 {
			res = append(res, a[dq[0]])
		}
	}
	return res
}
