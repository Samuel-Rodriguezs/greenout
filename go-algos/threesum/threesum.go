// Pacote threesum encontra trincas que somam um alvo com dois ponteiros.
package threesum

import "sort"

// Trincas devolve todas as trincas únicas (a <= b <= c) de valores de nums que
// somam alvo, em ordem lexicográfica. Cada elemento é usado no máximo uma vez
// por trinca (por posição). nums não é alterado.
func Trincas(nums []int, alvo int) [][3]int {
	v := append([]int(nil), nums...)
	sort.Ints(v)
	var res [][3]int
	for i := 0; i+2 < len(v); i++ {
		if i > 0 && v[i] == v[i-1] {
			continue
		}
		for l, r := i+1, len(v)-1; l < r; {
			switch s := v[i] + v[l] + v[r]; {
			case s < alvo:
				l++
			case s > alvo:
				r--
			default:
				res = append(res, [3]int{v[i], v[l], v[r]})
				for l < r && v[l] == v[l+1] {
					l++
				}
				for l < r && v[r] == v[r-1] {
					r--
				}
				l++
				r--
			}
		}
	}
	return res
}

// SomaZero é o caso clássico: trincas que somam zero.
func SomaZero(nums []int) [][3]int { return Trincas(nums, 0) }
