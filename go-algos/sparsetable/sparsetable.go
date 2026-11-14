// Pacote sparsetable implementa consultas de mínimo em intervalo (RMQ) com
// pré-processamento O(n log n) e consulta O(1).
package sparsetable

import "math/bits"

// Tabela guarda os mínimos de blocos de tamanho potência de dois.
type Tabela struct {
	t [][]int
}

// Nova constrói a tabela para o vetor a (que não é modificado).
func Nova(a []int) *Tabela {
	n := len(a)
	if n == 0 {
		return &Tabela{}
	}
	niveis := bits.Len(uint(n))
	t := make([][]int, niveis)
	t[0] = append([]int(nil), a...)
	for k := 1; k < niveis; k++ {
		tam := n - (1 << k) + 1
		t[k] = make([]int, tam)
		for i := 0; i < tam; i++ {
			t[k][i] = min(t[k-1][i], t[k-1][i+(1<<(k-1))])
		}
	}
	return &Tabela{t: t}
}

// Minimo devolve o menor valor em [l, r] (inclusive). ok=false se o intervalo
// for inválido.
func (s *Tabela) Minimo(l, r int) (int, bool) {
	if len(s.t) == 0 || l < 0 || r >= len(s.t[0]) || l > r {
		return 0, false
	}
	k := bits.Len(uint(r-l+1)) - 1
	return min(s.t[k][l], s.t[k][r-(1<<k)+1]), true
}
