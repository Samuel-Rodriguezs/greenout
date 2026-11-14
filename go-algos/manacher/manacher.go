// Pacote manacher encontra palíndromos em tempo linear (algoritmo de Manacher).
package manacher

// raios calcula, para cada centro, o raio dos palíndromos ímpares (d1, inclui o
// centro) e pares (d2, centro entre i-1 e i).
func raios(s []rune) (d1, d2 []int) {
	n := len(s)
	d1, d2 = make([]int, n), make([]int, n)
	for i, l, r := 0, 0, -1; i < n; i++ {
		k := 1
		if i <= r {
			k = min(d1[l+r-i], r-i+1)
		}
		for i-k >= 0 && i+k < n && s[i-k] == s[i+k] {
			k++
		}
		d1[i] = k
		if i+k-1 > r {
			l, r = i-k+1, i+k-1
		}
	}
	for i, l, r := 0, 0, -1; i < n; i++ {
		k := 0
		if i <= r {
			k = min(d2[l+r-i+1], r-i+1)
		}
		for i+k < n && i-k-1 >= 0 && s[i+k] == s[i-k-1] {
			k++
		}
		d2[i] = k
		if i+k-1 > r {
			l, r = i-k, i+k-1
		}
	}
	return d1, d2
}

// MaiorPalindromo devolve o maior substring palindrômico de s (o mais à
// esquerda em caso de empate).
func MaiorPalindromo(s string) string {
	r := []rune(s)
	if len(r) == 0 {
		return ""
	}
	d1, d2 := raios(r)
	melhorIni, melhorTam := 0, 0
	for i := range r {
		if tam := 2*d1[i] - 1; tam > melhorTam {
			melhorIni, melhorTam = i-d1[i]+1, tam
		}
		if tam := 2 * d2[i]; tam > melhorTam {
			melhorIni, melhorTam = i-d2[i], tam
		}
	}
	return string(r[melhorIni : melhorIni+melhorTam])
}

// Contar devolve quantos substrings (por posição) de s são palíndromos.
func Contar(s string) int {
	d1, d2 := raios([]rune(s))
	total := 0
	for i := range d1 {
		total += d1[i] + d2[i]
	}
	return total
}
