package lab

import (
	"math/rand"
	"reflect"
	"slices"
	"testing"
)

func TestOrdenacoes(t *testing.T) {
	casos := []struct {
		nome  string
		dados []int
		want  []int
	}{
		{"vazio", []int{}, []int{}},
		{"um", []int{1}, []int{1}},
		{"ordenado", []int{1, 2, 3, 4}, []int{1, 2, 3, 4}},
		{"inverso", []int{4, 3, 2, 1}, []int{1, 2, 3, 4}},
		{"duplicados", []int{3, 1, 3, 1, 2, 2}, []int{1, 1, 2, 2, 3, 3}},
		{"iguais", []int{7, 7, 7, 7}, []int{7, 7, 7, 7}},
		{"negativos", []int{0, -5, 3, -1}, []int{-5, -1, 0, 3}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			original := slices.Clone(c.dados)
			if got := OrdenarQuick(c.dados); !reflect.DeepEqual(got, c.want) {
				t.Errorf("quick got %v want %v", got, c.want)
			}
			if got := OrdenarMerge(c.dados); !reflect.DeepEqual(got, c.want) {
				t.Errorf("merge got %v want %v", got, c.want)
			}
			if !reflect.DeepEqual(c.dados, original) {
				t.Errorf("entrada alterada: %v", c.dados)
			}
		})
	}
}

func TestOrdenacoesAleatorio(t *testing.T) {
	r := rand.New(rand.NewSource(42))
	for k := 0; k < 50; k++ {
		dados := make([]int, r.Intn(200))
		for i := range dados {
			dados[i] = r.Intn(50) - 25
		}
		want := slices.Clone(dados)
		slices.Sort(want)
		if got := OrdenarQuick(dados); !slices.Equal(got, want) {
			t.Fatalf("quick falhou para %v", dados)
		}
		if got := OrdenarMerge(dados); !slices.Equal(got, want) {
			t.Fatalf("merge falhou para %v", dados)
		}
	}
}

func TestOrdenacoesStrings(t *testing.T) {
	got := OrdenarMerge([]string{"c", "a", "b"})
	if !reflect.DeepEqual(got, []string{"a", "b", "c"}) {
		t.Fatalf("got %v", got)
	}
}
