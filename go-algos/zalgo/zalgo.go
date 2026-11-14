// Pacote zalgo implementa o algoritmo Z para casamento de padrões.
package zalgo

// Z devolve o vetor z onde z[i] é o tamanho do maior prefixo de s que começa
// em i. Por convenção z[0] = len(s).
func Z(s string) []int {
	n := len(s)
	z := make([]int, n)
	if n == 0 {
		return z
	}
	z[0] = n
	for i, l, r := 1, 0, 0; i < n; i++ {
		if i < r {
			z[i] = min(r-i, z[i-l])
		}
		for i+z[i] < n && s[z[i]] == s[i+z[i]] {
			z[i]++
		}
		if i+z[i] > r {
			l, r = i, i+z[i]
		}
	}
	return z
}

// Buscar devolve os índices de todas as ocorrências de p em s.
func Buscar(s, p string) []int {
	if p == "" || len(p) > len(s) {
		return nil
	}
	// '\x00' separa padrão e texto; padrões que contenham esse byte não são suportados.
	z := Z(p + "\x00" + s)
	var res []int
	for i := len(p) + 1; i < len(z); i++ {
		if z[i] == len(p) {
			res = append(res, i-len(p)-1)
		}
	}
	return res
}
