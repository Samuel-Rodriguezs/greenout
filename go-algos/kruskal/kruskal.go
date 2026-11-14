// Pacote kruskal calcula a árvore geradora mínima ordenando as arestas.
package kruskal

import (
	"sort"

	"greenout/algos/unionfind"
)

// Aresta não dirigida ponderada.
type Aresta struct {
	U, V, Peso int
}

// AGM devolve o peso total, as arestas escolhidas e se o grafo é conexo.
// Para grafos desconexos devolve a floresta geradora mínima e ok=false.
func AGM(n int, arestas []Aresta) (total int, escolhidas []Aresta, ok bool) {
	ord := append([]Aresta(nil), arestas...)
	sort.SliceStable(ord, func(i, j int) bool { return ord[i].Peso < ord[j].Peso })
	uf := unionfind.Novo(n)
	for _, a := range ord {
		if uf.Unir(a.U, a.V) {
			total += a.Peso
			escolhidas = append(escolhidas, a)
		}
	}
	return total, escolhidas, n == 0 || uf.Componentes == 1
}
