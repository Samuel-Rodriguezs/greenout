package lab

// CrivoPrimos devolve todos os primos <= limite (crivo de Eratóstenes).
func CrivoPrimos(limite int) []int {
	if limite < 2 {
		return []int{}
	}
	composto := make([]bool, limite+1)
	for i := 2; i*i <= limite; i++ {
		if composto[i] {
			continue
		}
		for j := i * i; j <= limite; j += i {
			composto[j] = true
		}
	}
	primos := []int{}
	for i := 2; i <= limite; i++ {
		if !composto[i] {
			primos = append(primos, i)
		}
	}
	return primos
}
