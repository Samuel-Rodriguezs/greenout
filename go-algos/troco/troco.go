// Pacote troco resolve o problema do troco por programação dinâmica.
package troco

// Minimo devolve o menor número de moedas que somam valor e as moedas usadas
// (ordem crescente). Devolve -1 e nil se for impossível.
func Minimo(moedas []int, valor int) (int, []int) {
	if valor < 0 {
		return -1, nil
	}
	const inf = int(^uint(0) >> 2)
	dp := make([]int, valor+1)
	ult := make([]int, valor+1)
	for v := 1; v <= valor; v++ {
		dp[v] = inf
		for _, m := range moedas {
			if m > 0 && m <= v && dp[v-m]+1 < dp[v] {
				dp[v] = dp[v-m] + 1
				ult[v] = m
			}
		}
	}
	if dp[valor] >= inf {
		return -1, nil
	}
	var usadas []int
	for v := valor; v > 0; v -= ult[v] {
		usadas = append(usadas, ult[v])
	}
	// ordena em ordem crescente (inserção, o vetor é pequeno)
	for i := 1; i < len(usadas); i++ {
		for j := i; j > 0 && usadas[j-1] > usadas[j]; j-- {
			usadas[j-1], usadas[j] = usadas[j], usadas[j-1]
		}
	}
	return dp[valor], usadas
}

// Formas conta de quantas maneiras (combinações, sem ordem) é possível
// formar valor com as moedas.
func Formas(moedas []int, valor int) int {
	if valor < 0 {
		return 0
	}
	dp := make([]int, valor+1)
	dp[0] = 1
	for _, m := range moedas {
		if m <= 0 {
			continue
		}
		for v := m; v <= valor; v++ {
			dp[v] += dp[v-m]
		}
	}
	return dp[valor]
}
