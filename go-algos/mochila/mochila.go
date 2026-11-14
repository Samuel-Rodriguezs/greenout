// Pacote mochila resolve a mochila 0/1 e a mochila ilimitada por programação dinâmica.
package mochila

// Zero1 devolve o valor máximo e os índices dos itens escolhidos (cada item
// no máximo uma vez) respeitando a capacidade.
func Zero1(pesos, valores []int, capacidade int) (int, []int) {
	n := min(len(pesos), len(valores))
	if capacidade < 0 {
		return 0, nil
	}
	dp := make([][]int, n+1)
	for i := range dp {
		dp[i] = make([]int, capacidade+1)
	}
	for i := 1; i <= n; i++ {
		for c := 0; c <= capacidade; c++ {
			dp[i][c] = dp[i-1][c]
			if pesos[i-1] <= c {
				dp[i][c] = max(dp[i][c], dp[i-1][c-pesos[i-1]]+valores[i-1])
			}
		}
	}
	var itens []int
	for i, c := n, capacidade; i > 0; i-- {
		if dp[i][c] != dp[i-1][c] {
			itens = append(itens, i-1)
			c -= pesos[i-1]
		}
	}
	for i, j := 0, len(itens)-1; i < j; i, j = i+1, j-1 {
		itens[i], itens[j] = itens[j], itens[i]
	}
	return dp[n][capacidade], itens
}

// Ilimitada devolve o valor máximo permitindo repetir itens. Itens de peso
// não positivo são ignorados.
func Ilimitada(pesos, valores []int, capacidade int) int {
	if capacidade < 0 {
		return 0
	}
	dp := make([]int, capacidade+1)
	for c := 1; c <= capacidade; c++ {
		for i := 0; i < min(len(pesos), len(valores)); i++ {
			if pesos[i] > 0 && pesos[i] <= c {
				dp[c] = max(dp[c], dp[c-pesos[i]]+valores[i])
			}
		}
	}
	return dp[capacidade]
}
