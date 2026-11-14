package parser

import (
	"strings"
	"testing"

	"greenout/comp/ast"
)

func analisarOK(t *testing.T, fonte string) *ast.Programa {
	t.Helper()
	prog, erros := Analisar(fonte)
	if len(erros) > 0 {
		t.Fatalf("erros inesperados em %q: %v", fonte, erros)
	}
	return prog
}

func TestPrecedencia(t *testing.T) {
	casos := []struct{ fonte, quer string }{
		{"1 + 2 * 3;", "(1 + (2 * 3))"},
		{"1 * 2 + 3;", "((1 * 2) + 3)"},
		{"1 - 2 - 3;", "((1 - 2) - 3)"},
		{"(1 + 2) * 3;", "((1 + 2) * 3)"},
		{"-1 + 2;", "((-1) + 2)"},
		{"!a && b;", "((!a) && b)"},
		{"a || b && c;", "(a || (b && c))"},
		{"a == b || c != d;", "((a == b) || (c != d))"},
		{"1 + 2 < 3 + 4;", "((1 + 2) < (3 + 4))"},
		{"a < b == c < d;", "((a < b) == (c < d))"},
		{"a % b * c;", "((a % b) * c)"},
		{"--a;", "(-(-a))"},
		{"-a * b;", "((-a) * b)"},
		{"-f(x);", "(-f(x))"},
		{"f(1, 2 + 3)(4);", "f(1, (2 + 3))(4)"},
		{"a[1 + 1][2];", "((a[(1 + 1)])[2])"},
		{"a[0] + b[1] * 2;", "((a[0]) + ((b[1]) * 2))"},
		{"[1, 2 + 3, [4]];", "[1, (2 + 3), [4]]"},
		{"[];", "[]"},
		{"f();", "f()"},
		{`"a" + "b";`, `("a" + "b")`},
		{"fn(a, b) { return a; }(1, 2);", "fn(a, b) {...}(1, 2)"},
		{"1 <= 2 && 3 >= 4;", "((1 <= 2) && (3 >= 4))"},
	}
	for _, c := range casos {
		t.Run(c.fonte, func(t *testing.T) {
			prog := analisarOK(t, c.fonte)
			if len(prog.Comandos) != 1 {
				t.Fatalf("comandos = %d, quer 1", len(prog.Comandos))
			}
			ce, ok := prog.Comandos[0].(*ast.ComandoExpr)
			if !ok {
				t.Fatalf("tipo = %T, quer *ast.ComandoExpr", prog.Comandos[0])
			}
			if got := ce.Expr.String(); got != c.quer {
				t.Errorf("String() = %q, quer %q", got, c.quer)
			}
		})
	}
}

func TestComandos(t *testing.T) {
	casos := []struct {
		nome   string
		fonte  string
		verifi func(t *testing.T, c ast.Comando)
	}{
		{"let", "let x = 1 + 2;", func(t *testing.T, c ast.Comando) {
			l := c.(*ast.Let)
			if l.Nome.Nome != "x" || l.Valor.String() != "(1 + 2)" {
				t.Errorf("let = %s %s", l.Nome.Nome, l.Valor)
			}
		}},
		{"atribuicao", "x = 3;", func(t *testing.T, c ast.Comando) {
			a := c.(*ast.Atribuicao)
			if a.Alvo.String() != "x" || a.Valor.String() != "3" {
				t.Errorf("atribuição = %s = %s", a.Alvo, a.Valor)
			}
		}},
		{"atribuicao indice", "a[i + 1] = 9;", func(t *testing.T, c ast.Comando) {
			a := c.(*ast.Atribuicao)
			if a.Alvo.String() != "(a[(i + 1)])" {
				t.Errorf("alvo = %s", a.Alvo)
			}
		}},
		{"return valor", "return 5;", func(t *testing.T, c ast.Comando) {
			if r := c.(*ast.Retorno); r.Valor.String() != "5" {
				t.Errorf("valor = %s", r.Valor)
			}
		}},
		{"return vazio", "return;", func(t *testing.T, c ast.Comando) {
			if r := c.(*ast.Retorno); r.Valor != nil {
				t.Errorf("valor = %v, quer nil", r.Valor)
			}
		}},
		{"if sem else", "if (a) { b; }", func(t *testing.T, c ast.Comando) {
			s := c.(*ast.Se)
			if s.Senao != nil || len(s.Entao.Comandos) != 1 {
				t.Errorf("se = %+v", s)
			}
		}},
		{"if else", "if (a) { 1; } else { 2; 3; }", func(t *testing.T, c ast.Comando) {
			s := c.(*ast.Se)
			if b, ok := s.Senao.(*ast.Bloco); !ok || len(b.Comandos) != 2 {
				t.Errorf("senao = %#v", s.Senao)
			}
		}},
		{"else if", "if (a) { } else if (b) { } else { }", func(t *testing.T, c ast.Comando) {
			s := c.(*ast.Se)
			s2, ok := s.Senao.(*ast.Se)
			if !ok {
				t.Fatalf("senao = %T, quer *ast.Se", s.Senao)
			}
			if _, ok := s2.Senao.(*ast.Bloco); !ok {
				t.Errorf("senao interno = %T", s2.Senao)
			}
		}},
		{"while", "while (i < 10) { i = i + 1; }", func(t *testing.T, c ast.Comando) {
			w := c.(*ast.Enquanto)
			if w.Cond.String() != "(i < 10)" || len(w.Corpo.Comandos) != 1 {
				t.Errorf("enquanto = %+v", w)
			}
		}},
		{"declaracao de funcao", "fn soma(a, b) { return a + b; }", func(t *testing.T, c ast.Comando) {
			f := c.(*ast.DeclFuncao)
			if f.Nome.Nome != "soma" || len(f.Params) != 2 || f.Params[1].Nome != "b" {
				t.Errorf("função = %+v", f)
			}
		}},
		{"funcao sem parametros", "fn f() { }", func(t *testing.T, c ast.Comando) {
			if f := c.(*ast.DeclFuncao); len(f.Params) != 0 {
				t.Errorf("params = %v", f.Params)
			}
		}},
		{"funcao anonima em let", "let f = fn(x) { return x; };", func(t *testing.T, c ast.Comando) {
			if _, ok := c.(*ast.Let).Valor.(*ast.LiteralFuncao); !ok {
				t.Errorf("valor = %T", c.(*ast.Let).Valor)
			}
		}},
		{"bloco solto", "{ let a = 1; }", func(t *testing.T, c ast.Comando) {
			if b := c.(*ast.Bloco); len(b.Comandos) != 1 {
				t.Errorf("bloco = %+v", b)
			}
		}},
		{"comentarios", "// oi\nlet a = 1; // fim\n", func(t *testing.T, c ast.Comando) {
			if _, ok := c.(*ast.Let); !ok {
				t.Errorf("tipo = %T", c)
			}
		}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			prog := analisarOK(t, c.fonte)
			if len(prog.Comandos) != 1 {
				t.Fatalf("comandos = %d, quer 1", len(prog.Comandos))
			}
			c.verifi(t, prog.Comandos[0])
		})
	}
}

func TestPosicoesNos(t *testing.T) {
	prog := analisarOK(t, "let x = 1;\nx = a / b;")
	atrib := prog.Comandos[1].(*ast.Atribuicao)
	if p := atrib.Valor.Pos(); p.Linha != 2 || p.Coluna != 7 { // posição do operador '/'
		t.Errorf("pos do infixo = %v, quer 2:7", p)
	}
	if p := prog.Comandos[0].Pos(); p.Linha != 1 || p.Coluna != 1 {
		t.Errorf("pos do let = %v", p)
	}
}

func TestErrosSintaxe(t *testing.T) {
	casos := []struct {
		nome  string
		fonte string
		quer  []string // mensagens completas esperadas, na ordem
	}{
		{"falta ponto e virgula", "let x = 1\nlet y = 2;", []string{"2:1: esperado ';', encontrado 'let'"}},
		{"let sem nome", "let = 5;", []string{"1:5: esperado 'IDENT', encontrado '='"}},
		{"let sem igual", "let x 5;", []string{"1:7: esperado '=', encontrado número 5"}},
		{"expressao faltando", "let x = ;", []string{"1:9: expressão esperada, encontrado ';'"}},
		{"parentese nao fechado", "(1 + 2;", []string{"1:7: esperado ')', encontrado ';'"}},
		{"if sem parenteses", "if x { }", []string{"1:4: esperado '(', encontrado identificador 'x'"}},
		{"bloco nao fechado", "while (a) { b;", []string{"1:15: esperado '}', encontrado fim do arquivo"}},
		{"chaves extras", "}", []string{"1:1: expressão esperada, encontrado '}'"}},
		{"atribuicao invalida", "1 = 2;", []string{"1:1: alvo de atribuição inválido"}},
		{"atribuicao a chamada", "f(x) = 2;", []string{"1:2: alvo de atribuição inválido"}},
		{"atribuicao encadeada", "a = b = 1;", []string{"1:7: esperado ';', encontrado '='"}},
		{"caractere ilegal", "let x = @;", []string{"1:9: caractere inesperado '@'"}},
		{"texto nao terminado", "let s = \"abc;", []string{"1:9: texto não terminado"}},
		{"inteiro grande", "let n = 99999999999999999999;", []string{"1:9: inteiro fora do intervalo: 99999999999999999999"}},
		{"parametro invalido", "fn f(1) {}", []string{"1:6: esperado 'IDENT', encontrado número 1"}},
		{"array nao fechado", "[1, 2;", []string{"1:6: esperado ']', encontrado ';'"}},
		{"chamada nao fechada", "f(1, 2;", []string{"1:7: esperado ')', encontrado ';'"}},
		{"recuperacao com varios erros", "let a = ;\nlet b = 2;\nlet = 3;\nlet c = ;", []string{
			"1:9: expressão esperada, encontrado ';'",
			"3:5: esperado 'IDENT', encontrado '='",
			"4:9: expressão esperada, encontrado ';'",
		}},
		{"erro dentro de bloco continua depois", "fn f() { let = 1; return 2; }\nlet z = ;", []string{
			"1:14: esperado 'IDENT', encontrado '='",
			"2:9: expressão esperada, encontrado ';'",
		}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			_, erros := Analisar(c.fonte)
			if len(erros) != len(c.quer) {
				t.Fatalf("erros = %v, quer %v", erros, c.quer)
			}
			for i, e := range erros {
				if e.Error() != c.quer[i] {
					t.Errorf("erro %d = %q, quer %q", i, e.Error(), c.quer[i])
				}
			}
		})
	}
}

func TestPrecedenciaOp(t *testing.T) {
	if !(PrecedenciaOp("*") > PrecedenciaOp("+") && PrecedenciaOp("+") > PrecedenciaOp("<") &&
		PrecedenciaOp("<") > PrecedenciaOp("==") && PrecedenciaOp("==") > PrecedenciaOp("&&") &&
		PrecedenciaOp("&&") > PrecedenciaOp("||") && PrecedenciaOp("||") > 0) {
		t.Error("ordem de precedência incorreta")
	}
	if PrecedenciaOp("?") != 0 || PrecPrefixo <= PrecedenciaOp("*") {
		t.Error("precedência de desconhecido/prefixo incorreta")
	}
}

// Entradas malformadas devem terminar sem pânico e sem laço infinito.
func TestRobustez(t *testing.T) {
	entradas := []string{
		"", ";", ";;;", "}}}", "{{{", "(((", ")))", "fn", "fn(", "fn f", "fn f(", "fn f(a", "fn f(a,",
		"let", "let x", "let x =", "if", "if (", "if (a)", "if (a) {", "else", "while", "return",
		"a[", "a[1", "f(", "[", "\"", "@@@", "1 2 3", "let let let", "- - -", "!", "a = ",
		strings.Repeat("(", 5000), strings.Repeat("-", 5000) + "1;", strings.Repeat("[", 3000),
	}
	for _, e := range entradas {
		_, erros := Analisar(e)
		if e != "" && len(erros) == 0 {
			t.Errorf("entrada %.20q deveria gerar erro", e)
		}
	}
}
