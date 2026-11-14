// Pacote unionfind implementa conjuntos disjuntos com compressão de caminho
// e união por posto.
package unionfind

// UF representa uma coleção de conjuntos disjuntos sobre 0..n-1.
type UF struct {
	pai         []int
	posto       []int
	Componentes int
}

// Novo cria n conjuntos unitários.
func Novo(n int) *UF {
	u := &UF{pai: make([]int, n), posto: make([]int, n), Componentes: n}
	for i := range u.pai {
		u.pai[i] = i
	}
	return u
}

// Achar devolve o representante de x, comprimindo o caminho.
func (u *UF) Achar(x int) int {
	raiz := x
	for u.pai[raiz] != raiz {
		raiz = u.pai[raiz]
	}
	for u.pai[x] != raiz {
		u.pai[x], x = raiz, u.pai[x]
	}
	return raiz
}

// Unir junta os conjuntos de a e b. Devolve false se já estavam juntos.
func (u *UF) Unir(a, b int) bool {
	ra, rb := u.Achar(a), u.Achar(b)
	if ra == rb {
		return false
	}
	if u.posto[ra] < u.posto[rb] {
		ra, rb = rb, ra
	}
	u.pai[rb] = ra
	if u.posto[ra] == u.posto[rb] {
		u.posto[ra]++
	}
	u.Componentes--
	return true
}

// Conectados informa se a e b pertencem ao mesmo conjunto.
func (u *UF) Conectados(a, b int) bool { return u.Achar(a) == u.Achar(b) }
