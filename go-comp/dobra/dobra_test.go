package dobra

import (
	"testing"

	"greenout/comp/ast"
	"greenout/comp/impressor"
	"greenout/comp/parser"
)

func dobrar(t *testing.T, fonte string) (string, int) {
	t.Helper()
	prog, erros := parser.Analisar(fonte)
	if len(erros) > 0 {
		t.Fatalf("erros: %v", erros)
	}
	n := Programa(prog)
	return impressor.Formatar(prog), n
}

func TestDobrar(t *testing.T) {
	casos := []struct {
		nome   string
		fonte  string
		quer   string
		dobras int
	}{
		{"soma", "let x = 1 + 2;", "let x = 3;\n", 1},
		{"precedencia", "let x = 2 + 3 * 4;", "let x = 14;\n", 2},
		{"parenteses", "let x = (2 + 3) * 4 - 1;", "let x = 19;\n", 3},
		{"divisao e resto", "let x = 17 / 5 + 17 % 5;", "let x = 5;\n", 3},
		{"negativo", "let x = -(3 + 4);", "let x = -7;\n", 2},
		{"duplo negativo", "let x = --5;", "let x = 5;\n", 2},
		{"comparacoes", "let a = 1 < 2; let b = 3 >= 4; let c = 2 == 2; let d = 2 != 2;",
			"let a = true;\nlet b = false;\nlet c = true;\nlet d = false;\n", 4},
		{"texto", `let s = "ab" + "cd";`, "let s = \"abcd\";\n", 1},
		{"comparar texto", `let a = "a" < "b"; let b = "x" == "y";`, "let a = true;\nlet b = false;\n", 2},
		{"negacao", "let a = !true; let b = !!false;", "let a = false;\nlet b = false;\n", 3},
		{"logicos", "let a = true && false; let b = false || true;", "let a = false;\nlet b = true;\n", 2},
		{"curto circuito descarta direita", "let a = false && f(); let b = true || f();", "let a = false;\nlet b = true;\n", 2},
		{"curto circuito nao descarta", "let a = true && f(); let b = false || f();", "let a = true && f();\nlet b = false || f();\n", 0},
		{"divisao por zero preservada", "let a = 1 / 0; let b = 5 % 0;", "let a = 1 / 0;\nlet b = 5 % 0;\n", 0},
		{"parcial", "let y = x + (1 + 2);", "let y = x + 3;\n", 1},
		{"nao mistura tipos", `let y = 1 + "a";`, "let y = 1 + \"a\";\n", 0},
		{"variaveis intactas", "let y = a + b * 2;", "let y = a + b * 2;\n", 0},
		{"em argumentos e arrays", "print(1 + 1, [2 * 2, 3]);", "print(2, [4, 3]);\n", 2},
		{"em indices e atribuicoes", "a[1 + 1] = 2 * 3;", "a[2] = 6;\n", 2},
		{"em condicoes", "if (1 < 2) { while (3 > 4) { x = 1 + 1; } }", "if (true) {\n  while (false) {\n    x = 2;\n  }\n}\n", 3},
		{"em funcoes", "fn f() { return 2 * 3; } let g = fn() { return 4 - 1; };", "fn f() {\n  return 6;\n}\nlet g = fn() {\n  return 3;\n};\n", 2},
		{"em return e else", "fn f(x) { if (x) { return 1 + 1; } else { return 2 + 2; } }",
			"fn f(x) {\n  if (x) {\n    return 2;\n  } else {\n    return 4;\n  }\n}\n", 2},
		{"estouro com wrap", "let x = 9223372036854775807 + 1;", "let x = -9223372036854775808;\n", 1},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			got, n := dobrar(t, c.fonte)
			if got != c.quer {
				t.Errorf("saída =\n%s\nquer\n%s", got, c.quer)
			}
			if n != c.dobras {
				t.Errorf("dobras = %d, quer %d", n, c.dobras)
			}
		})
	}
}

func TestExpressaoIsolada(t *testing.T) {
	prog, _ := parser.Analisar("(1 + 2) * x;")
	e := prog.Comandos[0].(*ast.ComandoExpr).Expr
	r, n := Expressao(e)
	if n != 1 || r.String() != "(3 * x)" {
		t.Errorf("Expressao = %s (%d dobras)", r, n)
	}
	r, n = Expressao(&ast.Inteiro{Valor: 7})
	if n != 0 || r.String() != "7" {
		t.Errorf("literal deveria ficar intacto: %s %d", r, n)
	}
}

func TestPosicaoPreservada(t *testing.T) {
	prog, _ := parser.Analisar("let x = 4 /\n  2;")
	Programa(prog)
	lit, ok := prog.Comandos[0].(*ast.Let).Valor.(*ast.Inteiro)
	if !ok || lit.Valor != 2 {
		t.Fatalf("esperado literal 2, veio %v", prog.Comandos[0].(*ast.Let).Valor)
	}
	if lit.Posicao.Linha != 1 || lit.Posicao.Coluna != 11 {
		t.Errorf("posição = %v, quer a do operador 1:11", lit.Posicao)
	}
}
