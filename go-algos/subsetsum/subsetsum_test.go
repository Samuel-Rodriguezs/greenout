package subsetsum

import "testing"

func TestSubconjunto(t *testing.T) {
	casos := []struct {
		nome string
		nums []int
		alvo int
		ok   bool
	}{
		{"clássico", []int{3, 34, 4, 12, 5, 2}, 9, true},
		{"impossível", []int{3, 34, 4, 12, 5, 2}, 30, false},
		{"alvo zero", []int{5, 6}, 0, true},
		{"vazio alvo positivo", nil, 1, false},
		{"vazio alvo zero", nil, 0, true},
		{"alvo negativo", []int{1}, -1, false},
		{"soma total", []int{1, 2, 3}, 6, true},
		{"com zeros", []int{0, 0, 7}, 7, true},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			idx, ok := Subconjunto(c.nums, c.alvo)
			if ok != c.ok || Existe(c.nums, c.alvo) != c.ok {
				t.Fatalf("ok=%v", ok)
			}
			soma := 0
			vistos := map[int]bool{}
			for _, i := range idx {
				if vistos[i] {
					t.Fatalf("índice repetido %d", i)
				}
				vistos[i] = true
				soma += c.nums[i]
			}
			if ok && soma != c.alvo {
				t.Errorf("soma=%d, alvo=%d", soma, c.alvo)
			}
		})
	}
}

func TestPartilhaIgual(t *testing.T) {
	casos := []struct {
		nums []int
		want bool
	}{
		{[]int{1, 5, 11, 5}, true},
		{[]int{1, 2, 3, 5}, false},
		{nil, true},
		{[]int{7}, false},
		{[]int{2, 2}, true},
		{[]int{-1, 1}, false},
	}
	for _, c := range casos {
		if got := PartilhaIgual(c.nums); got != c.want {
			t.Errorf("PartilhaIgual(%v)=%v, esperado %v", c.nums, got, c.want)
		}
	}
}
