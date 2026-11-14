// Pacote fatias oferece utilitários genéricos para slices.
package fatias

// Mapear aplica f a cada elemento e devolve um novo slice.
func Mapear[T, R any](s []T, f func(T) R) []R {
	r := make([]R, 0, len(s))
	for _, v := range s {
		r = append(r, f(v))
	}
	return r
}

// Filtrar devolve os elementos para os quais f retorna true.
func Filtrar[T any](s []T, f func(T) bool) []T {
	r := []T{}
	for _, v := range s {
		if f(v) {
			r = append(r, v)
		}
	}
	return r
}

// Reduzir acumula os elementos a partir de um valor inicial.
func Reduzir[T, A any](s []T, inicial A, f func(A, T) A) A {
	acc := inicial
	for _, v := range s {
		acc = f(acc, v)
	}
	return acc
}

// AgruparPor agrupa os elementos pela chave calculada, preservando a ordem.
func AgruparPor[T any, K comparable](s []T, chave func(T) K) map[K][]T {
	m := make(map[K][]T)
	for _, v := range s {
		k := chave(v)
		m[k] = append(m[k], v)
	}
	return m
}

// Particionar divide s em blocos de tamanho n (o último pode ser menor).
// Retorna nil se n <= 0. Os blocos não compartilham memória com s.
func Particionar[T any](s []T, n int) [][]T {
	if n <= 0 {
		return nil
	}
	r := make([][]T, 0, (len(s)+n-1)/n)
	for i := 0; i < len(s); i += n {
		fim := min(i+n, len(s))
		r = append(r, append([]T(nil), s[i:fim]...))
	}
	return r
}

// Unicos remove duplicatas mantendo a primeira ocorrência.
func Unicos[T comparable](s []T) []T {
	vistos := make(map[T]struct{}, len(s))
	r := []T{}
	for _, v := range s {
		if _, ok := vistos[v]; ok {
			continue
		}
		vistos[v] = struct{}{}
		r = append(r, v)
	}
	return r
}
