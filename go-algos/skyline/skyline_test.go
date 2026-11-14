package skyline

import (
	"math/rand"
	"reflect"
	"testing"
)

func TestContorno(t *testing.T) {
	casos := []struct {
		nome    string
		predios []Predio
		want    []Ponto
	}{
		{"clássico", []Predio{{2, 9, 10}, {3, 7, 15}, {5, 12, 12}, {15, 20, 10}, {19, 24, 8}},
			[]Ponto{{2, 10}, {3, 15}, {7, 12}, {12, 0}, {15, 10}, {20, 8}, {24, 0}}},
		{"mesmo intervalo", []Predio{{0, 2, 3}, {0, 2, 3}}, []Ponto{{0, 3}, {2, 0}}},
		{"adjacentes mesma altura", []Predio{{0, 2, 3}, {2, 5, 3}}, []Ponto{{0, 3}, {5, 0}}},
		{"adjacentes alturas diferentes", []Predio{{0, 2, 3}, {2, 5, 4}}, []Ponto{{0, 3}, {2, 4}, {5, 0}}},
		{"um prédio", []Predio{{1, 3, 5}}, []Ponto{{1, 5}, {3, 0}}},
		{"aninhado", []Predio{{0, 10, 5}, {2, 4, 3}}, []Ponto{{0, 5}, {10, 0}}},
		{"vazio", nil, nil},
		{"inválidos ignorados", []Predio{{3, 3, 4}, {5, 2, 4}, {1, 2, 0}}, nil},
		{"mesmo início", []Predio{{0, 5, 2}, {0, 3, 4}}, []Ponto{{0, 4}, {3, 2}, {5, 0}}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := Contorno(c.predios); !reflect.DeepEqual(got, c.want) {
				t.Errorf("got %v, esperado %v", got, c.want)
			}
		})
	}
}

// alturaEm calcula a altura em x por força bruta.
func alturaEm(predios []Predio, x int) int {
	h := 0
	for _, p := range predios {
		if p.E <= x && x < p.D {
			h = max(h, p.Altura)
		}
	}
	return h
}

func TestAleatorioContraForcaBruta(t *testing.T) {
	r := rand.New(rand.NewSource(9))
	for it := 0; it < 200; it++ {
		var ps []Predio
		for i := r.Intn(8); i > 0; i-- {
			e := r.Intn(20)
			ps = append(ps, Predio{e, e + 1 + r.Intn(10), 1 + r.Intn(10)})
		}
		cont := Contorno(ps)
		j, atual := 0, 0
		for x := 0; x < 35; x++ {
			for j < len(cont) && cont[j].X == x {
				atual = cont[j].Y
				j++
			}
			if want := alturaEm(ps, x); atual != want {
				t.Fatalf("predios=%v x=%d altura=%d, esperado %d (contorno %v)", ps, x, atual, want, cont)
			}
		}
		for k := 1; k < len(cont); k++ {
			if cont[k].X <= cont[k-1].X || cont[k].Y == cont[k-1].Y {
				t.Fatalf("contorno mal-formado: %v", cont)
			}
		}
	}
}
