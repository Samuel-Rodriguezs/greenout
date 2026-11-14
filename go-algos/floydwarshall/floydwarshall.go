// Pacote floydwarshall calcula caminhos mínimos entre todos os pares.
package floydwarshall

// Inf representa ausência de aresta/caminho.
const Inf = int(^uint(0) >> 2)

// TodosPares recebe a matriz de adjacência (Inf = sem aresta) e devolve a
// matriz de distâncias mínimas e se há ciclo negativo. A entrada não é alterada.
func TodosPares(m [][]int) ([][]int, bool) {
	n := len(m)
	d := make([][]int, n)
	for i := range m {
		d[i] = append([]int(nil), m[i]...)
		if d[i][i] > 0 {
			d[i][i] = 0
		}
	}
	for k := 0; k < n; k++ {
		for i := 0; i < n; i++ {
			if d[i][k] == Inf {
				continue
			}
			for j := 0; j < n; j++ {
				if d[k][j] != Inf && d[i][k]+d[k][j] < d[i][j] {
					d[i][j] = d[i][k] + d[k][j]
				}
			}
		}
	}
	for i := 0; i < n; i++ {
		if d[i][i] < 0 {
			return d, true
		}
	}
	return d, false
}
