// Pacote skyline resolve o problema do contorno de prédios (skyline) com
// varredura de eventos e heap máximo com remoção preguiçosa.
package skyline

import (
	"container/heap"
	"sort"
)

// Predio ocupa o intervalo [E, D) com altura Altura.
type Predio struct {
	E, D, Altura int
}

// Ponto do contorno: a partir de X a altura passa a ser Y.
type Ponto struct{ X, Y int }

type heapMax []int

func (h heapMax) Len() int           { return len(h) }
func (h heapMax) Less(i, j int) bool { return h[i] > h[j] }
func (h heapMax) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }
func (h *heapMax) Push(x any)        { *h = append(*h, x.(int)) }
func (h *heapMax) Pop() any {
	v := *h
	x := v[len(v)-1]
	*h = v[:len(v)-1]
	return x
}

type evento struct {
	x, h int // h < 0: início de prédio de altura -h; h > 0: fim
}

// Contorno devolve os pontos-chave do contorno, ordenados por X. Prédios com
// largura ou altura não positivas são ignorados.
func Contorno(predios []Predio) []Ponto {
	var evs []evento
	for _, p := range predios {
		if p.D > p.E && p.Altura > 0 {
			evs = append(evs, evento{p.E, -p.Altura}, evento{p.D, p.Altura})
		}
	}
	sort.Slice(evs, func(i, j int) bool {
		if evs[i].x != evs[j].x {
			return evs[i].x < evs[j].x
		}
		return evs[i].h < evs[j].h // inícios mais altos primeiro; fins mais baixos primeiro
	})
	h := &heapMax{0}
	remover := map[int]int{}
	var res []Ponto
	anterior := 0
	for _, e := range evs {
		if e.h < 0 {
			heap.Push(h, -e.h)
		} else {
			remover[e.h]++
		}
		for remover[(*h)[0]] > 0 {
			remover[(*h)[0]]--
			heap.Pop(h)
		}
		if atual := (*h)[0]; atual != anterior {
			res = append(res, Ponto{e.x, atual})
			anterior = atual
		}
	}
	return res
}
