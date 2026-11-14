// Pacote toposort implementa ordenação topológica por Kahn e por DFS.
package toposort

// Kahn devolve uma ordem topológica do grafo dirigido (lista de adjacência)
// ou ok=false se houver ciclo.
func Kahn(adj [][]int) (ordem []int, ok bool) {
	n := len(adj)
	grau := make([]int, n)
	for _, vs := range adj {
		for _, v := range vs {
			grau[v]++
		}
	}
	fila := make([]int, 0, n)
	for v, g := range grau {
		if g == 0 {
			fila = append(fila, v)
		}
	}
	for i := 0; i < len(fila); i++ {
		u := fila[i]
		ordem = append(ordem, u)
		for _, v := range adj[u] {
			if grau[v]--; grau[v] == 0 {
				fila = append(fila, v)
			}
		}
	}
	if len(ordem) != n {
		return nil, false
	}
	return ordem, true
}

// DFS devolve uma ordem topológica pelo pós-ordem invertido da busca em
// profundidade, ou ok=false se houver ciclo.
func DFS(adj [][]int) (ordem []int, ok bool) {
	const (
		branco = iota
		cinza
		preto
	)
	n := len(adj)
	cor := make([]int, n)
	pos := make([]int, 0, n)
	var visita func(u int) bool
	visita = func(u int) bool {
		cor[u] = cinza
		for _, v := range adj[u] {
			switch cor[v] {
			case cinza:
				return false
			case branco:
				if !visita(v) {
					return false
				}
			}
		}
		cor[u] = preto
		pos = append(pos, u)
		return true
	}
	for u := 0; u < n; u++ {
		if cor[u] == branco && !visita(u) {
			return nil, false
		}
	}
	for i, j := 0, len(pos)-1; i < j; i, j = i+1, j-1 {
		pos[i], pos[j] = pos[j], pos[i]
	}
	return pos, true
}
