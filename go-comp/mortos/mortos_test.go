package mortos

import (
	"testing"

	"greenout/comp/dobra"
	"greenout/comp/impressor"
	"greenout/comp/parser"
)

func eliminar(t *testing.T, fonte string, comDobra bool) (string, int) {
	t.Helper()
	prog, erros := parser.Analisar(fonte)
	if len(erros) > 0 {
		t.Fatalf("erros: %v", erros)
	}
	if comDobra {
		dobra.Programa(prog)
	}
	n := Eliminar(prog)
	return impressor.Formatar(prog), n
}

func TestEliminar(t *testing.T) {
	casos := []struct {
		nome   string
		fonte  string
		dobrar bool
		quer   string
		n      int
	}{
		{"if true", "if (true) { x = 1; } else { x = 2; }", false, "x = 1;\n", 2},
		{"if false com else", "if (false) { x = 1; } else { x = 2; }", false, "x = 2;\n", 2},
		{"if false sem else", "if (false) { x = 1; }", false, "", 1},
		{"if true com declaracao mantem escopo", "if (true) { let a = 1; print(a); }", false, "{\n  let a = 1;\n  print(a);\n}\n", 1},
		{"else if constante", "if (c) { x = 1; } else if (true) { x = 2; } else { x = 3; }", false,
			"if (c) {\n  x = 1;\n} else {\n  x = 2;\n}\n", 2},
		{"else if falso e sem else", "if (c) { x = 1; } else if (false) { x = 2; }", false, "if (c) {\n  x = 1;\n}\n", 1},
		{"com dobra de constantes", "if (1 < 2) { x = 1; } else { x = 2; }", true, "x = 1;\n", 2},
		{"while false", "while (false) { x = 1; } y = 2;", false, "y = 2;\n", 1},
		{"while com condicao dobrada", "while (1 > 2) { x = 1; }", true, "", 1},
		{"while normal intacto", "while (i < 3) { i = i + 1; }", false, "while (i < 3) {\n  i = i + 1;\n}\n", 0},
		{"expressoes sem efeito", "1; \"a\"; x; true; [1, 2]; fn() { }; f(); a + b;", false, "f();\na + b;\n", 6},
		{"apos return", "fn f() { return 1; x = 2; print(x); }", false, "fn f() {\n  return 1;\n}\n", 2},
		{"apos return com funcao declarada preserva cauda", "fn f() { return g(); fn g() { return 1; } }", false,
			"fn f() {\n  return g();\n  fn g() {\n    return 1;\n  }\n}\n", 0},
		{"return em bloco aninhado achatado", "fn f() { { return 1; } x = 2; }", false, "fn f() {\n  return 1;\n}\n", 2},
		{"bloco vazio", "{ } x = 1; { { } }", false, "x = 1;\n", 3},
		{"funcao anonima processada", "let f = fn() { if (true) { return 1; } return 2; };", false, "let f = fn() {\n  return 1;\n};\n", 3},
		{"funcao anonima em argumento", "run(fn() { 1; return 2; 3; });", false, "run(fn() {\n  return 2;\n});\n", 2},
		{"recursivo em if aninhado", "while (a) { if (false) { b = 1; } c = 2; }", false, "while (a) {\n  c = 2;\n}\n", 1},
		{"nada a fazer", "let a = 1; print(a);", false, "let a = 1;\nprint(a);\n", 0},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			got, n := eliminar(t, c.fonte, c.dobrar)
			if got != c.quer {
				t.Errorf("saída =\n%q\nquer\n%q", got, c.quer)
			}
			if n != c.n {
				t.Errorf("remoções = %d, quer %d", n, c.n)
			}
		})
	}
}

func TestIdempotente(t *testing.T) {
	fonte := "fn f(x) { if (true) { return x; } 1; } while (false) { } { }"
	prog, _ := parser.Analisar(fonte)
	Eliminar(prog)
	antes := impressor.Formatar(prog)
	if n := Eliminar(prog); n != 0 {
		t.Errorf("segunda passada removeu %d", n)
	}
	if depois := impressor.Formatar(prog); depois != antes {
		t.Errorf("mudou na segunda passada:\n%s\n%s", antes, depois)
	}
}
