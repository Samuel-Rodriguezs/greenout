package elevador

import (
	"errors"
	"reflect"
	"testing"
)

func TestAtendimento(t *testing.T) {
	casos := []struct {
		nome     string
		inicio   int
		chamadas []int
		ordem    []string
		passos   int
	}{
		{"uma subida", 0, []int{3}, []string{"3"}, 4},
		{"varredura sobe e depois desce", 2, []int{5, 1, 4}, []string{"4", "5", "1"}, 10},
		{"já no andar", 3, []int{3}, []string{"3"}, 1},
		{"duplicadas contam uma vez", 0, []int{2, 2}, []string{"2"}, 3},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			e, _ := Novo(10)
			e.Andar = c.inicio
			for _, a := range c.chamadas {
				if err := e.Chamar(a); err != nil {
					t.Fatal(err)
				}
			}
			passos := e.Executar()
			if !reflect.DeepEqual(e.Log, c.ordem) {
				t.Errorf("ordem = %v, esperada %v", e.Log, c.ordem)
			}
			if passos != c.passos {
				t.Errorf("passos = %d, esperados %d", passos, c.passos)
			}
			if e.Dir != Parado || e.Pendentes() {
				t.Error("deveria terminar parado e sem pendências")
			}
		})
	}
}

func TestChamadaDuranteMovimento(t *testing.T) {
	e, _ := Novo(10)
	e.Chamar(5)
	e.Passo() // andar 1
	e.Passo() // andar 2
	e.Chamar(3)
	e.Executar()
	if want := []string{"3", "5"}; !reflect.DeepEqual(e.Log, want) {
		t.Errorf("ordem = %v, esperada %v", e.Log, want)
	}
}

func TestParadoSemChamadas(t *testing.T) {
	e, _ := Novo(5)
	if e.Passo() || e.Andar != 0 || e.Dir != Parado {
		t.Error("elevador sem chamadas não deveria se mover")
	}
}

func TestErros(t *testing.T) {
	if _, err := Novo(0); !errors.Is(err, ErrAndarInvalido) {
		t.Errorf("erro = %v", err)
	}
	e, _ := Novo(5)
	for _, a := range []int{-1, 6} {
		if err := e.Chamar(a); !errors.Is(err, ErrAndarInvalido) {
			t.Errorf("Chamar(%d): erro = %v", a, err)
		}
	}
}
