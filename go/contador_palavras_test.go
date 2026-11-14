package lab

import (
	"reflect"
	"testing"
)

func TestPalavrasContar(t *testing.T) {
	casos := []struct {
		nome  string
		texto string
		want  map[string]int
	}{
		{"vazio", "", map[string]int{}},
		{"so pontuacao", " ,.; -- ", map[string]int{}},
		{"basico", "a b a", map[string]int{"a": 2, "b": 1}},
		{"maiusculas", "Go go GO", map[string]int{"go": 3}},
		{"pontuacao", "Olá, mundo! Olá.", map[string]int{"olá": 2, "mundo": 1}},
		{"hifen", "guarda-chuva e guarda-chuva", map[string]int{"guarda-chuva": 2, "e": 1}},
		{"quebras", "um\ndois\tum", map[string]int{"um": 2, "dois": 1}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := PalavrasContar(c.texto); !reflect.DeepEqual(got, c.want) {
				t.Fatalf("got %v, want %v", got, c.want)
			}
		})
	}
}
