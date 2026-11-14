package impressor

import (
	"testing"

	"greenout/comp/parser"
)

func analisar(t *testing.T, fonte string) string {
	t.Helper()
	prog, erros := parser.Analisar(fonte)
	if len(erros) > 0 {
		t.Fatalf("erros ao analisar %q: %v", fonte, erros)
	}
	return Formatar(prog)
}

func TestFormatar(t *testing.T) {
	casos := []struct {
		nome  string
		fonte string
		quer  string
	}{
		{"let simples", "let   x=1+2;", "let x = 1 + 2;\n"},
		{"precedencia sem parenteses", "let x = 1 + (2 * 3);", "let x = 1 + 2 * 3;\n"},
		{"parenteses necessarios", "let x = (1 + 2) * 3;", "let x = (1 + 2) * 3;\n"},
		{"associatividade esquerda", "x = a - (b - c);", "x = a - (b - c);\n"},
		{"associatividade esquerda sem parens", "x = (a - b) - c;", "x = a - b - c;\n"},
		{"prefixo", "x = -(a + b);", "x = -(a + b);\n"},
		{"prefixo duplo", "x = !!a;", "x = !!a;\n"},
		{"alvo parentesizado", "x = (a + b)[0];", "x = (a + b)[0];\n"},
		{"chamada e indice", "f(1,2)[0](3);", "f(1, 2)[0](3);\n"},
		{"array", "let a=[1,[2,3],\"x\"];", "let a = [1, [2, 3], \"x\"];\n"},
		{"texto com escapes", `print("a\"b\\c\n\t");`, "print(\"a\\\"b\\\\c\\n\\t\");\n"},
		{"atribuicao de indice", "a[i+1]=a[i];", "a[i + 1] = a[i];\n"},
		{"return vazio", "return;", "return;\n"},
		{"funcao", "fn soma(a,b){return a+b;}", "fn soma(a, b) {\n  return a + b;\n}\n"},
		{"funcao vazia", "fn f(){}", "fn f() {}\n"},
		{"if else if else", "if(a){x=1;}else if(b){x=2;}else{x=3;}",
			"if (a) {\n  x = 1;\n} else if (b) {\n  x = 2;\n} else {\n  x = 3;\n}\n"},
		{"while aninhado", "while(i<3){if(i==1){print(i);}i=i+1;}",
			"while (i < 3) {\n  if (i == 1) {\n    print(i);\n  }\n  i = i + 1;\n}\n"},
		{"funcao anonima", "let f=fn(x){return x*2;};", "let f = fn(x) {\n  return x * 2;\n};\n"},
		{"bloco solto", "{let a=1;}", "{\n  let a = 1;\n}\n"},
		{"logicos", "x = a && b || c && !d;", "x = a && b || c && !d;\n"},
		{"ou dentro de e", "x = a && (b || c);", "x = a && (b || c);\n"},
		{"vazio", "", ""},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := analisar(t, c.fonte); got != c.quer {
				t.Errorf("Formatar =\n%q\nquer\n%q", got, c.quer)
			}
		})
	}
}

// Formatar deve ser idempotente e produzir código que reanalisa.
func TestIdempotente(t *testing.T) {
	programas := []string{
		"let a = (1 + 2) * (3 - 4) / 5 % 6;",
		"x = a - (b - c) + -(d * e);",
		"fn fat(n){ if(n<=1){return 1;} return n*fat(n-1); } print(fat(5));",
		"let f = fn(a){ return fn(b){ return a + b; }; }; f(1)(2);",
		"let s = \"linha\\n\\\"citada\\\"\"; if (s == \"x\" || !(1 < 2)) { s = s + \"!\"; }",
		"while (i < n && (a[i] != 0 || b)) { a[i] = a[i + 1]; i = i + 1; }",
		"x = (a + b)(c)[d];",
	}
	for _, src := range programas {
		prog1, erros := parser.Analisar(src)
		if len(erros) > 0 {
			t.Fatalf("%q: %v", src, erros)
		}
		f1 := Formatar(prog1)
		prog2, erros := parser.Analisar(f1)
		if len(erros) > 0 {
			t.Fatalf("saída formatada não reanalisa: %v\n%s", erros, f1)
		}
		if f2 := Formatar(prog2); f2 != f1 {
			t.Errorf("não idempotente:\n%s\n---\n%s", f1, f2)
		}
		if len(prog1.Comandos) != len(prog2.Comandos) {
			t.Errorf("número de comandos mudou: %d -> %d", len(prog1.Comandos), len(prog2.Comandos))
		}
	}
}
