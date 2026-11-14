// Pacote kmp implementa a busca de padrões de Knuth-Morris-Pratt.
package kmp

// Prefixo calcula a tabela de falhas (função prefixo) do padrão p.
func Prefixo(p string) []int {
	pi := make([]int, len(p))
	for i, k := 1, 0; i < len(p); i++ {
		for k > 0 && p[i] != p[k] {
			k = pi[k-1]
		}
		if p[i] == p[k] {
			k++
		}
		pi[i] = k
	}
	return pi
}

// Buscar devolve os índices (em bytes) de todas as ocorrências de p em s,
// inclusive sobrepostas. Padrão vazio não tem ocorrências.
func Buscar(s, p string) []int {
	if p == "" || len(p) > len(s) {
		return nil
	}
	pi := Prefixo(p)
	var res []int
	for i, k := 0, 0; i < len(s); i++ {
		for k > 0 && (k == len(p) || s[i] != p[k]) {
			k = pi[k-1]
		}
		if s[i] == p[k] {
			k++
		}
		if k == len(p) {
			res = append(res, i-len(p)+1)
		}
	}
	return res
}
