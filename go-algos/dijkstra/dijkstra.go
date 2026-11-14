// Pacote dijkstra calcula caminhos mínimos de fonte única com pesos não negativos.
package dijkstra

import "container/heap"

// Inf representa distância infinita (vértice inalcançável).
const Inf = int(^uint(0) >> 1)

// Aresta é uma aresta ponderada de saída.
type Aresta struct {
	Para int
	Peso int
}

type item struct{ no, dist int }

type fila []item

func (f fila) Len() int           { return len(f) }
func (f fila) Less(i, j int) bool { return f[i].dist < f[j].dist }
func (f fila) Swap(i, j int)      { f[i], f[j] = f[j], f[i] }
func (f *fila) Push(x any)        { *f = append(*f, x.(item)) }
func (f *fila) Pop() any {
	v := *f
	x := v[len(v)-1]
	*f = v[:len(v)-1]
	return x
}

// MenoresCaminhos devolve as distâncias a partir de origem e o vetor de
// predecessores (-1 quando não há). Pesos negativos não são suportados.
func MenoresCaminhos(grafo [][]Aresta, origem int) (dist, pai []int) {
	n := len(grafo)
	dist = make([]int, n)
	pai = make([]int, n)
	for i := range dist {
		dist[i], pai[i] = Inf, -1
	}
	if origem < 0 || origem >= n {
		return dist, pai
	}
	dist[origem] = 0
	f := &fila{{origem, 0}}
	for f.Len() > 0 {
		cur := heap.Pop(f).(item)
		if cur.dist > dist[cur.no] {
			continue
		}
		for _, a := range grafo[cur.no] {
			if nd := cur.dist + a.Peso; nd < dist[a.Para] {
				dist[a.Para] = nd
				pai[a.Para] = cur.no
				heap.Push(f, item{a.Para, nd})
			}
		}
	}
	return dist, pai
}

// Caminho reconstrói o caminho até destino a partir do vetor de predecessores.
// Devolve nil se destino for inalcançável.
func Caminho(dist, pai []int, destino int) []int {
	if destino < 0 || destino >= len(dist) || dist[destino] == Inf {
		return nil
	}
	var c []int
	for v := destino; v != -1; v = pai[v] {
		c = append(c, v)
	}
	for i, j := 0, len(c)-1; i < j; i, j = i+1, j-1 {
		c[i], c[j] = c[j], c[i]
	}
	return c
}
