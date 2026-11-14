// Pacote nrainhas conta e encontra soluções do problema das N rainhas com bitmasks.
package nrainhas

// Contar devolve o número de maneiras de posicionar n rainhas em um tabuleiro
// n x n sem ataques. Suporta n até 31.
func Contar(n int) int {
	if n < 0 || n > 31 {
		return 0
	}
	todas := (1 << n) - 1
	var busca func(colunas, diag1, diag2 int) int
	busca = func(colunas, diag1, diag2 int) int {
		if colunas == todas {
			return 1
		}
		total := 0
		livres := todas &^ (colunas | diag1 | diag2)
		for livres != 0 {
			bit := livres & -livres
			livres ^= bit
			total += busca(colunas|bit, ((diag1|bit)<<1)&todas, (diag2|bit)>>1)
		}
		return total
	}
	return busca(0, 0, 0)
}

// Uma devolve a primeira solução (lexicograficamente): resp[linha] = coluna.
func Uma(n int) ([]int, bool) {
	if n <= 0 {
		return nil, n == 0
	}
	col := make([]int, n)
	usadaCol := make([]bool, n)
	d1 := make([]bool, 2*n)
	d2 := make([]bool, 2*n)
	var coloca func(l int) bool
	coloca = func(l int) bool {
		if l == n {
			return true
		}
		for c := 0; c < n; c++ {
			if usadaCol[c] || d1[l+c] || d2[l-c+n] {
				continue
			}
			usadaCol[c], d1[l+c], d2[l-c+n] = true, true, true
			col[l] = c
			if coloca(l + 1) {
				return true
			}
			usadaCol[c], d1[l+c], d2[l-c+n] = false, false, false
		}
		return false
	}
	if !coloca(0) {
		return nil, false
	}
	return col, true
}
