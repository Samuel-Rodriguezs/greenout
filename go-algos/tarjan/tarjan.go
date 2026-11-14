// Pacote tarjan encontra componentes fortemente conexos (algoritmo de Tarjan).
package tarjan

// SCC devolve os componentes fortemente conexos do grafo dirigido. Os
// componentes saem em ordem topológica reversa (sumidouros primeiro).
func SCC(adj [][]int) [][]int {
	n := len(adj)
	indice := make([]int, n)
	baixo := make([]int, n)
	naPilha := make([]bool, n)
	for i := range indice {
		indice[i] = -1
	}
	var pilha []int
	var comps [][]int
	contador := 0

	var visita func(u int)
	visita = func(u int) {
		indice[u], baixo[u] = contador, contador
		contador++
		pilha = append(pilha, u)
		naPilha[u] = true
		for _, v := range adj[u] {
			if indice[v] == -1 {
				visita(v)
				baixo[u] = min(baixo[u], baixo[v])
			} else if naPilha[v] {
				baixo[u] = min(baixo[u], indice[v])
			}
		}
		if baixo[u] == indice[u] {
			var comp []int
			for {
				v := pilha[len(pilha)-1]
				pilha = pilha[:len(pilha)-1]
				naPilha[v] = false
				comp = append(comp, v)
				if v == u {
					break
				}
			}
			comps = append(comps, comp)
		}
	}
	for u := 0; u < n; u++ {
		if indice[u] == -1 {
			visita(u)
		}
	}
	return comps
}
