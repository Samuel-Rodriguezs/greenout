package sudoku

import "testing"

var puzzle = [9]string{
	"53..7....",
	"6..195...",
	".98....6.",
	"8...6...3",
	"4..8.3..1",
	"7...2...6",
	".6....28.",
	"...419..5",
	"....8..79",
}

var solucao = [9]string{
	"534678912",
	"672195348",
	"198342567",
	"859761423",
	"426853791",
	"713924856",
	"961537284",
	"287419635",
	"345286179",
}

func completaValida(g Grade) bool {
	for i := 0; i < 9; i++ {
		var l, c, b int
		for j := 0; j < 9; j++ {
			l |= 1 << g[i][j]
			c |= 1 << g[j][i]
			b |= 1 << g[(i/3)*3+j/3][(i%3)*3+j%3]
		}
		if l != 0x3FE || c != 0x3FE || b != 0x3FE {
			return false
		}
	}
	return true
}

func TestResolverClassico(t *testing.T) {
	g, ok := Ler(puzzle)
	if !ok {
		t.Fatal("falha ao ler")
	}
	original := g
	if !Resolver(&g) {
		t.Fatal("deveria resolver")
	}
	esperado, _ := Ler(solucao)
	if g != esperado {
		t.Errorf("solução diferente: %v", g)
	}
	if !completaValida(g) {
		t.Error("grade resolvida inválida")
	}
	for l := 0; l < 9; l++ {
		for c := 0; c < 9; c++ {
			if original[l][c] != 0 && original[l][c] != g[l][c] {
				t.Errorf("pista alterada em (%d,%d)", l, c)
			}
		}
	}
}

func TestGradeVazia(t *testing.T) {
	var g Grade
	if !Resolver(&g) || !completaValida(g) {
		t.Error("grade vazia deveria ser preenchida validamente")
	}
}

func TestJaResolvida(t *testing.T) {
	g, _ := Ler(solucao)
	if !Resolver(&g) {
		t.Error("grade completa e válida deveria passar")
	}
}

func TestInvalidas(t *testing.T) {
	casos := map[string][9]string{
		"repetido na linha":  {"55.......", ".........", ".........", ".........", ".........", ".........", ".........", ".........", "........."},
		"repetido na coluna": {"5........", "5........", ".........", ".........", ".........", ".........", ".........", ".........", "........."},
		"repetido na caixa":  {"5........", ".5.......", ".........", ".........", ".........", ".........", ".........", ".........", "........."},
		// 1..8 na linha 0 e um 9 na coluna 8 deixa a célula (0,8) sem candidato
		"sem solução": {"12345678.", ".........", ".........", ".........", ".........", ".........", ".........", ".........", "........9"},
	}
	for nome, linhas := range casos {
		t.Run(nome, func(t *testing.T) {
			g, ok := Ler(linhas)
			if !ok {
				t.Fatal("falha ao ler")
			}
			antes := g
			if Resolver(&g) {
				t.Error("não deveria resolver")
			}
			if g != antes {
				t.Error("grade deveria permanecer inalterada")
			}
		})
	}
}

func TestLerInvalido(t *testing.T) {
	ruim := puzzle
	ruim[0] = "53..7...x"
	if _, ok := Ler(ruim); ok {
		t.Error("caractere inválido deveria falhar")
	}
	ruim[0] = "53"
	if _, ok := Ler(ruim); ok {
		t.Error("linha curta deveria falhar")
	}
}

func BenchmarkResolver(b *testing.B) {
	base, _ := Ler(puzzle)
	for i := 0; i < b.N; i++ {
		g := base
		Resolver(&g)
	}
}
