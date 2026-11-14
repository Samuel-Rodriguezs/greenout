package lexer

import (
	"testing"

	"greenout/comp/token"
)

type par struct {
	tipo token.Tipo
	lit  string
}

func TestTokens(t *testing.T) {
	casos := []struct {
		nome     string
		fonte    string
		esperado []par
	}{
		{"vazio", "", nil},
		{"let", "let x = 5;", []par{{token.Let, "let"}, {token.Ident, "x"}, {token.Atribui, "="}, {token.Inteiro, "5"}, {token.PontoVirgula, ";"}}},
		{"operadores", "== != <= >= < > && || ! % / * - +", []par{
			{token.Igual, "=="}, {token.Diferente, "!="}, {token.MenorIgual, "<="}, {token.MaiorIgual, ">="},
			{token.Menor, "<"}, {token.Maior, ">"}, {token.E, "&&"}, {token.Ou, "||"}, {token.Nao, "!"},
			{token.Resto, "%"}, {token.Barra, "/"}, {token.Asterisco, "*"}, {token.Menos, "-"}, {token.Mais, "+"}}},
		{"delimitadores", "(){}[],;", []par{
			{token.ParenAbre, "("}, {token.ParenFecha, ")"}, {token.ChaveAbre, "{"}, {token.ChaveFecha, "}"},
			{token.ColcheteAbre, "["}, {token.ColcheteFecha, "]"}, {token.Virgula, ","}, {token.PontoVirgula, ";"}}},
		{"palavras", "fn if else while return true false iff", []par{
			{token.Fn, "fn"}, {token.Se, "if"}, {token.Senao, "else"}, {token.Enquanto, "while"},
			{token.Retorna, "return"}, {token.Verdadeiro, "true"}, {token.Falso, "false"}, {token.Ident, "iff"}}},
		{"comentario", "1 // ignorado\n2", []par{{token.Inteiro, "1"}, {token.Inteiro, "2"}}},
		{"comentario no fim", "x // fim", []par{{token.Ident, "x"}}},
		{"texto", `"olá\n\"mundo\"\\"`, []par{{token.Texto, "olá\n\"mundo\"\\"}}},
		{"texto vazio", `""`, []par{{token.Texto, ""}}},
		{"ident com underscore", "_a1 b_2", []par{{token.Ident, "_a1"}, {token.Ident, "b_2"}}},
		{"texto nao terminado", "\"abc\nx", []par{{token.Ilegal, "texto não terminado"}, {token.Ident, "x"}}},
		{"escape invalido", `"a\qb"`, []par{{token.Ilegal, `escape inválido '\q'`}}},
		{"caractere invalido", "@", []par{{token.Ilegal, "caractere inesperado '@'"}}},
		{"e simples", "a & b", []par{{token.Ident, "a"}, {token.Ilegal, "caractere inesperado '&' (use '&&')"}, {token.Ident, "b"}}},
		{"numero colado em letra", "12ab", []par{{token.Ilegal, "número inválido 12ab"}}},
		{"runa multibyte", "é", []par{{token.Ilegal, "caractere inesperado 'é'"}}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			toks := Tokens(c.fonte)
			if ult := toks[len(toks)-1]; ult.Tipo != token.FimArquivo {
				t.Fatalf("último token = %v, quer FimArquivo", ult)
			}
			toks = toks[:len(toks)-1]
			if len(toks) != len(c.esperado) {
				t.Fatalf("quantidade = %d (%v), quer %d", len(toks), toks, len(c.esperado))
			}
			for i, e := range c.esperado {
				if toks[i].Tipo != e.tipo || toks[i].Literal != e.lit {
					t.Errorf("token %d = %v, quer %v %q", i, toks[i], e.tipo, e.lit)
				}
			}
		})
	}
}

func TestPosicoes(t *testing.T) {
	fonte := "let a = 1;\n  // c\n\tfoo(\"é\", ç)"
	casos := []struct {
		indice        int
		linha, coluna int
		deslocamento  int
	}{
		{0, 1, 1, 0},   // let
		{1, 1, 5, 4},   // a
		{4, 1, 10, 9},  // ;
		{5, 3, 2, 19},  // foo
		{6, 3, 5, 22},  // (
		{7, 3, 6, 23},  // "é"
		{8, 3, 9, 27},  // ,
		{9, 3, 11, 29}, // ç ilegal
	}
	toks := Tokens(fonte)
	for _, c := range casos {
		p := toks[c.indice].Pos
		if p.Linha != c.linha || p.Coluna != c.coluna || p.Deslocamento != c.deslocamento {
			t.Errorf("token %d (%v): pos = %+v, quer %d:%d off %d", c.indice, toks[c.indice], p, c.linha, c.coluna, c.deslocamento)
		}
	}
}

func TestFimRepetido(t *testing.T) {
	l := Novo("x")
	l.Proximo()
	for i := 0; i < 3; i++ {
		if tk := l.Proximo(); tk.Tipo != token.FimArquivo {
			t.Fatalf("esperado FimArquivo, veio %v", tk)
		}
	}
}
