// Pacote prim calcula a árvore geradora mínima crescendo a partir de um vértice.
package prim

import "container/heap"

// Aresta de saída em lista de adjacência (grafo não dirigido: inclua as duas direções).
type Aresta struct {
	Para, Peso int
}

type item struct{ no, peso, de int }

type fila []item

func (f fila) Len() int           { return len(f) }
func (f fila) Less(i, j int) bool { return f[i].peso < f[j].peso }
func (f fila) Swap(i, j int)      { f[i], f[j] = f[j], f[i] }
func (f *fila) Push(x any)        { *f = append(*f, x.(item)) }
func (f *fila) Pop() any {
	v := *f
	x := v[len(v)-1]
	*f = v[:len(v)-1]
	return x
}

// AGM devolve o peso total, o vetor de pais (-1 na raiz) e se o grafo é conexo.
func AGM(grafo [][]Aresta) (total int, pai []int, ok bool) {
	n := len(grafo)
	pai = make([]int, n)
	for i := range pai {
		pai[i] = -1
	}
	if n == 0 {
		return 0, pai, true
	}
	visto := make([]bool, n)
	f := &fila{{0, 0, -1}}
	cont := 0
	for f.Len() > 0 {
		cur := heap.Pop(f).(item)
		if visto[cur.no] {
			continue
		}
		visto[cur.no] = true
		pai[cur.no] = cur.de
		total += cur.peso
		cont++
		for _, a := range grafo[cur.no] {
			if !visto[a.Para] {
				heap.Push(f, item{a.Para, a.Peso, cur.no})
			}
		}
	}
	return total, pai, cont == n
}
