package retry

import (
	"errors"
	"slices"
	"testing"
	"time"
)

var errFalha = errors.New("falha")

func TestEspera(t *testing.T) {
	casos := []struct {
		nome string
		c    Config
		n    int
		want time.Duration
	}{
		{"primeira", Config{Base: time.Second}, 1, time.Second},
		{"segunda dobra", Config{Base: time.Second}, 2, 2 * time.Second},
		{"quarta", Config{Base: time.Second}, 4, 8 * time.Second},
		{"fator 3", Config{Base: time.Second, Fator: 3}, 3, 9 * time.Second},
		{"teto", Config{Base: time.Second, Maximo: 5 * time.Second}, 6, 5 * time.Second},
		{"fator invalido vira 2", Config{Base: time.Second, Fator: 0.5}, 2, 2 * time.Second},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := c.c.Espera(c.n); got != c.want {
				t.Fatalf("got %v want %v", got, c.want)
			}
		})
	}
}

func TestExecutar(t *testing.T) {
	casos := []struct {
		nome      string
		cfg       Config
		falhasAte int // falha enquanto tentativa <= falhasAte
		err       func(error) bool
		chamadas  int
		esperas   []time.Duration
	}{
		{"sucesso direto", Config{Tentativas: 3, Base: time.Second}, 0, func(e error) bool { return e == nil }, 1, nil},
		{"sucesso na 3ª", Config{Tentativas: 5, Base: time.Second}, 2, func(e error) bool { return e == nil }, 3,
			[]time.Duration{time.Second, 2 * time.Second}},
		{"esgota", Config{Tentativas: 3, Base: time.Second}, 99, func(e error) bool {
			var ee *ErroEsgotado
			return errors.As(e, &ee) && ee.Tentativas == 3 && errors.Is(e, errFalha)
		}, 3, []time.Duration{time.Second, 2 * time.Second}},
		{"tentativas zero vira 1", Config{Base: time.Second}, 99, func(e error) bool { return errors.Is(e, errFalha) }, 1, nil},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			var esperas []time.Duration
			c.cfg.Dormir = func(d time.Duration) { esperas = append(esperas, d) }
			chamadas := 0
			err := Executar(c.cfg, func(n int) error {
				chamadas++
				if n <= c.falhasAte {
					return errFalha
				}
				return nil
			})
			if !c.err(err) {
				t.Fatalf("erro inesperado: %v", err)
			}
			if chamadas != c.chamadas {
				t.Fatalf("chamadas %d", chamadas)
			}
			if !slices.Equal(esperas, c.esperas) {
				t.Fatalf("esperas %v want %v", esperas, c.esperas)
			}
		})
	}
}

func TestPermanenteInterrompe(t *testing.T) {
	chamadas := 0
	err := Executar(Config{Tentativas: 5, Dormir: func(time.Duration) {}}, func(int) error {
		chamadas++
		return Permanente(errFalha)
	})
	if chamadas != 1 || !errors.Is(err, errFalha) {
		t.Fatalf("chamadas=%d err=%v", chamadas, err)
	}
	var ee *ErroEsgotado
	if errors.As(err, &ee) {
		t.Fatal("não deveria ser ErroEsgotado")
	}
}
