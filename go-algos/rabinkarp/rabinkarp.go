// Pacote rabinkarp implementa busca de padrões com hash rolante.
package rabinkarp

const (
	base = 257
	mod  = 1_000_000_007
)

// Buscar devolve os índices de todas as ocorrências de p em s. Colisões de
// hash são descartadas com comparação direta.
func Buscar(s, p string) []int {
	n, m := len(s), len(p)
	if m == 0 || m > n {
		return nil
	}
	pot := 1 // base^(m-1) mod mod
	for i := 0; i < m-1; i++ {
		pot = pot * base % mod
	}
	hp, hs := 0, 0
	for i := 0; i < m; i++ {
		hp = (hp*base + int(p[i])) % mod
		hs = (hs*base + int(s[i])) % mod
	}
	var res []int
	for i := 0; ; i++ {
		if hp == hs && s[i:i+m] == p {
			res = append(res, i)
		}
		if i+m >= n {
			break
		}
		hs = ((hs-int(s[i])*pot%mod+mod)*base + int(s[i+m])) % mod
	}
	return res
}
