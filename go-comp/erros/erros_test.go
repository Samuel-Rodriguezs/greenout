package erros

import (
	"errors"
	"fmt"
	"strings"
	"testing"

	"greenout/comp/parser"
	"greenout/comp/semantica"
	"greenout/comp/token"
)

func pos(l, c int) token.Posicao { return token.Posicao{Linha: l, Coluna: c} }

func TestTrecho(t *testing.T) {
	casos := []struct {
		nome  string
		fonte string
		pos   token.Posicao
		quer  string
	}{
		{"primeira linha", "let x = ;", pos(1, 9), "  |\n1 | let x = ;\n  |         ^"},
		{"coluna 1", "x", pos(1, 1), "  |\n1 | x\n  | ^"},
		{"linha do meio", "a;\nb + ;\nc;", pos(2, 5), "  |\n2 | b + ;\n  |     ^"},
		{"tabulacao preservada", "\tlet = 1;", pos(1, 6), "  |\n1 | \tlet = 1;\n  | \t    ^"},
		{"runas multibyte contam como uma coluna", "let é = ?;", pos(1, 9), "  |\n1 | let é = ?;\n  |         ^"},
		{"fim do arquivo apos quebra", "x\n", pos(2, 1), "  |\n2 | \n  | ^"},
		{"numero de linha com dois digitos", "1;\n2;\n3;\n4;\n5;\n6;\n7;\n8;\n9;\nxx yy;", pos(10, 4),
			"   |\n10 | xx yy;\n   |    ^"},
		{"crlf", "a;\r\nb c;", pos(2, 3), "  |\n2 | b c;\n  |   ^"},
		{"posicao invalida", "x", token.Posicao{}, ""},
		{"linha inexistente", "x", pos(9, 1), ""},
		{"coluna alem do fim", "ab", pos(1, 5), "  |\n1 | ab\n  |     ^"},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := Novo(c.fonte).Trecho(c.pos); got != c.quer {
				t.Errorf("Trecho =\n%q\nquer\n%q", got, c.quer)
			}
		})
	}
}

func TestFormatar(t *testing.T) {
	c := Novo("let x = ;\nprint(y);")
	c.Adicionar(Sintaxe, pos(1, 9), "expressão esperada, encontrado ';'")
	c.AdicionarAviso(Semantica, pos(2, 7), "variável 'y' suspeita")
	c.Adicionar(Execucao, token.Posicao{}, "falha geral")
	quer := `erro[sintaxe]: expressão esperada, encontrado ';'
 --> 1:9
  |
1 | let x = ;
  |         ^

aviso[semântica]: variável 'y' suspeita
 --> 2:7
  |
2 | print(y);
  |       ^

erro[execução]: falha geral

2 erro(s), 1 aviso(s)
`
	if got := c.Formatar(); got != quer {
		t.Errorf("Formatar =\n%s\nquer\n%s", got, quer)
	}
}

func TestContagemETemErros(t *testing.T) {
	c := Novo("")
	if c.TemErros() || c.Formatar() != "" {
		t.Error("coletor vazio não tem erros nem saída")
	}
	c.AdicionarAviso(Semantica, pos(1, 1), "só aviso")
	if c.TemErros() {
		t.Error("aviso não deve contar como erro")
	}
	c.Adicionar(Tipos, pos(1, 1), "erro")
	if e, a := c.Contagem(); e != 1 || a != 1 || !c.TemErros() {
		t.Errorf("contagem = %d erros, %d avisos", e, a)
	}
	if len(c.Itens()) != 2 {
		t.Errorf("itens = %d", len(c.Itens()))
	}
}

func TestAdicionarErro(t *testing.T) {
	c := Novo("a b")
	c.AdicionarErro(Execucao, nil)
	c.AdicionarErro(Execucao, token.Errorf(pos(1, 3), "com posição"))
	c.AdicionarErro(Compilacao, fmt.Errorf("embrulhado: %w", token.Errorf(pos(1, 1), "interno")))
	c.AdicionarErro(Execucao, errors.New("simples"))
	itens := c.Itens()
	if len(itens) != 3 {
		t.Fatalf("itens = %d, quer 3 (nil é ignorado)", len(itens))
	}
	quer := []Item{
		{Fase: Execucao, Pos: pos(1, 3), Msg: "com posição"},
		{Fase: Compilacao, Pos: pos(1, 1), Msg: "interno"},
		{Fase: Execucao, Msg: "simples"},
	}
	for i, q := range quer {
		if itens[i] != q {
			t.Errorf("item %d = %+v, quer %+v", i, itens[i], q)
		}
	}
}

func TestLimite(t *testing.T) {
	c := Novo("x")
	c.Limite = 2
	for i := 0; i < 5; i++ {
		c.Adicionar(Sintaxe, pos(1, 1), fmt.Sprintf("erro %d", i))
	}
	saida := c.Formatar()
	for _, quer := range []string{"erro 0", "erro 1", "... e mais 3 diagnóstico(s)", "5 erro(s), 0 aviso(s)"} {
		if !strings.Contains(saida, quer) {
			t.Errorf("saída deveria conter %q:\n%s", quer, saida)
		}
	}
	if strings.Contains(saida, "erro 2") {
		t.Errorf("saída não deveria exibir o 3º erro:\n%s", saida)
	}
}

// Integração: erros reais do parser e da semântica renderizados com trecho.
func TestIntegracaoComParserESemantica(t *testing.T) {
	fonte := "let a = 1;\nlet b = ;\nprint(a);"
	_, es := parser.Analisar(fonte)
	c := Novo(fonte)
	c.AdicionarTodos(Sintaxe, es)
	quer := "erro[sintaxe]: expressão esperada, encontrado ';'\n --> 2:9\n  |\n2 | let b = ;\n  |         ^\n\n1 erro(s), 0 aviso(s)\n"
	if got := c.Formatar(); got != quer {
		t.Errorf("Formatar =\n%s\nquer\n%s", got, quer)
	}

	fonte = "fn f() {\n  let sobra = 1;\n  return naoexiste;\n}"
	prog, _ := parser.Analisar(fonte)
	r := semantica.Analisar(prog, semantica.Opcoes{})
	c = Novo(fonte)
	c.AdicionarTodos(Semantica, r.Erros)
	c.AdicionarAvisos(Semantica, r.Avisos)
	if e, a := c.Contagem(); e != 1 || a != 1 {
		t.Fatalf("contagem = %d/%d\n%s", e, a, c.Formatar())
	}
	if saida := c.Formatar(); !strings.Contains(saida, "\n  | "+strings.Repeat(" ", 9)+"^") || !strings.Contains(saida, "return naoexiste;") {
		t.Errorf("trecho ausente:\n%s", saida)
	}
}
