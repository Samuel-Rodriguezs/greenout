// Pacote bellmanford calcula caminhos mínimos permitindo pesos negativos.
package bellmanford

import "errors"

// Inf representa distância infinita.
const Inf = int(^uint(0) >> 2)

// ErrCicloNegativo indica ciclo negativo alcançável a partir da origem.
var ErrCicloNegativo = errors.New("ciclo de peso negativo alcançável")

// Aresta é uma aresta dirigida ponderada.
type Aresta struct {
	De, Para, Peso int
}

// BellmanFord devolve as distâncias a partir de origem para um grafo de n vértices.
func BellmanFord(n int, arestas []Aresta, origem int) ([]int, error) {
	dist := make([]int, n)
	for i := range dist {
		dist[i] = Inf
	}
	if origem < 0 || origem >= n {
		return dist, nil
	}
	dist[origem] = 0
	for i := 0; i < n-1; i++ {
		mudou := false
		for _, a := range arestas {
			if dist[a.De] != Inf && dist[a.De]+a.Peso < dist[a.Para] {
				dist[a.Para] = dist[a.De] + a.Peso
				mudou = true
			}
		}
		if !mudou {
			return dist, nil
		}
	}
	for _, a := range arestas {
		if dist[a.De] != Inf && dist[a.De]+a.Peso < dist[a.Para] {
			return nil, ErrCicloNegativo
		}
	}
	return dist, nil
}
