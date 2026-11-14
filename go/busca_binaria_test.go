package lab

import "testing"

func TestBuscaBinariaIndice(t *testing.T) {
	casos := []struct {
		nome  string
		dados []int
		alvo  int
		idx   int
		ok    bool
	}{
		{"vazio", nil, 1, -1, false},
		{"unico achado", []int{5}, 5, 0, true},
		{"unico ausente", []int{5}, 4, -1, false},
		{"primeiro", []int{1, 3, 5, 7, 9}, 1, 0, true},
		{"ultimo", []int{1, 3, 5, 7, 9}, 9, 4, true},
		{"meio", []int{1, 3, 5, 7, 9}, 5, 2, true},
		{"menor que todos", []int{1, 3, 5}, 0, -1, false},
		{"maior que todos", []int{1, 3, 5}, 6, -1, false},
		{"entre elementos", []int{1, 3, 5}, 4, -1, false},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			idx, ok := BuscaBinariaIndice(c.dados, c.alvo)
			if idx != c.idx || ok != c.ok {
				t.Fatalf("got %d,%v want %d,%v", idx, ok, c.idx, c.ok)
			}
		})
	}
}

func TestBuscaBinariaIndiceStrings(t *testing.T) {
	dados := []string{"ana", "bia", "caio", "dani"}
	if idx, ok := BuscaBinariaIndice(dados, "caio"); !ok || idx != 2 {
		t.Fatalf("got %d,%v", idx, ok)
	}
	if _, ok := BuscaBinariaIndice(dados, "ze"); ok {
		t.Fatal("não deveria achar")
	}
}
