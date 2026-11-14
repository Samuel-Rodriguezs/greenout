// Pacote edmondskarp calcula o fluxo máximo (Ford-Fulkerson com BFS).
package edmondskarp

// Aresta dirigida com capacidade.
type Aresta struct {
	De, Para, Cap int
}

// FluxoMaximo devolve o fluxo máximo de s para t em uma rede de n vértices.
// Arestas paralelas têm as capacidades somadas.
func FluxoMaximo(n int, arestas []Aresta, s, t int) int {
	if s == t || s < 0 || t < 0 || s >= n || t >= n {
		return 0
	}
	cap := make([][]int, n)
	for i := range cap {
		cap[i] = make([]int, n)
	}
	adj := make([][]int, n)
	for _, a := range arestas {
		if a.De == a.Para {
			continue
		}
		if cap[a.De][a.Para] == 0 && cap[a.Para][a.De] == 0 {
			adj[a.De] = append(adj[a.De], a.Para)
			adj[a.Para] = append(adj[a.Para], a.De)
		}
		cap[a.De][a.Para] += a.Cap
	}
	total := 0
	pai := make([]int, n)
	for {
		for i := range pai {
			pai[i] = -1
		}
		pai[s] = s
		fila := []int{s}
		for len(fila) > 0 && pai[t] == -1 {
			u := fila[0]
			fila = fila[1:]
			for _, v := range adj[u] {
				if pai[v] == -1 && cap[u][v] > 0 {
					pai[v] = u
					fila = append(fila, v)
				}
			}
		}
		if pai[t] == -1 {
			return total
		}
		gargalo := int(^uint(0) >> 1)
		for v := t; v != s; v = pai[v] {
			gargalo = min(gargalo, cap[pai[v]][v])
		}
		for v := t; v != s; v = pai[v] {
			cap[pai[v]][v] -= gargalo
			cap[v][pai[v]] += gargalo
		}
		total += gargalo
	}
}
