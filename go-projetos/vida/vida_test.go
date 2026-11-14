package vida

import (
	"errors"
	"testing"
)

func TestProxima(t *testing.T) {
	casos := []struct {
		nome, antes, depois string
	}{
		{"bloco estável", "....\n.##.\n.##.\n....", "....\n.##.\n.##.\n...."},
		{"piscador", ".....\n..#..\n..#..\n..#..\n.....", ".....\n.....\n.###.\n.....\n....."},
		{"solitário morre", "...\n.#.\n...", "...\n...\n..."},
		{"planador", ".#....\n..#...\n###...\n......\n......\n......", "......\n#.#...\n.##...\n.#....\n......\n......"},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			g, err := DeTexto(c.antes)
			if err != nil {
				t.Fatal(err)
			}
			if got := g.Proxima().String(); got != c.depois {
				t.Errorf("got:\n%s\nwant:\n%s", got, c.depois)
			}
		})
	}
}

func TestToroide(t *testing.T) {
	g, _ := DeTexto("#..\n...\n..#")
	if !g.Viva(-1, -1) || !g.Viva(3, 3) || g.Viva(0, 1) {
		t.Error("coordenadas não dão a volta")
	}
}

func TestPopulacaoEImutabilidade(t *testing.T) {
	g, _ := DeTexto(".#.\n.#.\n.#.")
	g.Proxima()
	if g.Populacao() != 3 || g.String() != ".#.\n.#.\n.#." {
		t.Error("Proxima alterou a grade original")
	}
}

func TestErros(t *testing.T) {
	if _, err := Nova(0, 3); !errors.Is(err, ErrGrade) {
		t.Errorf("erro = %v", err)
	}
	if _, err := DeTexto("##\n#"); !errors.Is(err, ErrGrade) {
		t.Errorf("erro = %v", err)
	}
}
