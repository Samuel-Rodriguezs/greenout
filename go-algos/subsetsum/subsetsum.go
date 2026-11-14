// Pacote subsetsum resolve a soma de subconjuntos e a partição igual.
package subsetsum

// Existe informa se algum subconjunto de nums soma alvo (números não negativos).
func Existe(nums []int, alvo int) bool {
	_, ok := Subconjunto(nums, alvo)
	return ok
}

// Subconjunto devolve os índices de um subconjunto que soma alvo.
func Subconjunto(nums []int, alvo int) ([]int, bool) {
	if alvo < 0 {
		return nil, false
	}
	n := len(nums)
	dp := make([][]bool, n+1)
	for i := range dp {
		dp[i] = make([]bool, alvo+1)
		dp[i][0] = true
	}
	for i := 1; i <= n; i++ {
		for s := 0; s <= alvo; s++ {
			dp[i][s] = dp[i-1][s] || (nums[i-1] >= 0 && nums[i-1] <= s && dp[i-1][s-nums[i-1]])
		}
	}
	if !dp[n][alvo] {
		return nil, false
	}
	var idx []int
	for i, s := n, alvo; i > 0; i-- {
		if !dp[i-1][s] {
			idx = append(idx, i-1)
			s -= nums[i-1]
		}
	}
	for i, j := 0, len(idx)-1; i < j; i, j = i+1, j-1 {
		idx[i], idx[j] = idx[j], idx[i]
	}
	return idx, true
}

// PartilhaIgual informa se nums pode ser dividido em dois grupos de mesma soma.
func PartilhaIgual(nums []int) bool {
	total := 0
	for _, x := range nums {
		if x < 0 {
			return false
		}
		total += x
	}
	return total%2 == 0 && Existe(nums, total/2)
}
