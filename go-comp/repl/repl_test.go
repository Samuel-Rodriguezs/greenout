package repl

import (
	"strings"
	"testing"
)

func sessao(t *testing.T, entrada string) string {
	t.Helper()
	var saida strings.Builder
	if err := Executar(strings.NewReader(entrada), &saida); err != nil {
		t.Fatalf("Executar: %v", err)
	}
	return saida.String()
}

func TestSessoes(t *testing.T) {
	casos := []struct {
		nome    string
		entrada string
		quer    string
	}{
		{"vazio", "", ">> "},
		{"expressao sem ponto e virgula", "1 + 2\n", ">> 3\n>> "},
		{"expressao com ponto e virgula", "1 + 2;\n", ">> 3\n>> "},
		{"texto aparece entre aspas", "\"a\" + \"b\"\n", ">> \"ab\"\n>> "},
		{"array", "[1, \"x\", true]\n", ">> [1, \"x\", true]\n>> "},
		{"let nao imprime", "let x = 5;\n", ">> >> "},
		{"estado persiste", "let x = 5\nx * 2\nx = x + 1\nx\n", ">> >> 10\n>> >> 6\n>> "},
		{"print", "print(\"oi\", 1)\n", ">> oi 1\n>> "},
		{"linhas em branco sao ignoradas", "\n\n1\n", ">> >> >> 1\n>> "},
		{"funcao em varias linhas", "fn fat(n) {\n  if (n <= 1) { return 1; }\n  return n * fat(n - 1);\n}\nfat(5)\n",
			">> ... ... ... >> 120\n>> "},
		{"array em varias linhas", "let a = [\n1,\n2\n]\nlen(a)\n", ">> ... ... ... >> 2\n>> "},
		{"closure entre linhas", "fn mk() { let c = 0; return fn() { c = c + 1; return c; }; }\nlet f = mk()\nf()\nf()\n",
			">> >> >> 1\n>> 2\n>> "},
		{"funcao tem nome na repr", "fn f() {}\nf\nlen\n", ">> >> <função f>\n>> <embutido len>\n>> "},
		{"sair interrompe", "1\n:sair\n2\n", ">> 1\n>> "},
		{"atalho q", ":q\n1\n", ">> "},
		{"comando desconhecido", ":foo\n", ">> comando desconhecido \":foo\" (use :ajuda)\n>> "},
		{"ajuda", ":ajuda\n", ">> " + textoAjuda + ">> "},
		{"limpar esquece estado", "let x = 1\n:limpar\nx\n",
			">> >> estado limpo\n>> erro[execução]: variável 'x' não declarada\n --> 1:1\n  |\n1 | x;\n  | ^\n\n1 erro(s), 0 aviso(s)\n>> "},
		{"fmt", ":fmt let   a=1+2*3\n", ">> let a = 1 + 2 * 3;\n>> "},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := sessao(t, c.entrada); got != c.quer {
				t.Errorf("saída =\n%q\nquer\n%q", got, c.quer)
			}
		})
	}
}

func TestErrosNaSessao(t *testing.T) {
	casos := []struct {
		nome    string
		entrada string
		quer    []string // trechos que devem aparecer
	}{
		{"erro de sintaxe com trecho", "let x = ;\n", []string{
			"erro[sintaxe]: expressão esperada, encontrado ';'", " --> 1:9", "1 | let x = ;", "  |         ^"}},
		{"erro de execucao com trecho", "let a = [1, 2]\na[5]\n", []string{
			"erro[execução]: índice 5 fora dos limites (tamanho 2)", " --> 1:2", "1 | a[5];"}},
		{"divisao por zero em bloco multilinha", "{\n  let a = 1;\n  print(a / 0);\n}\n", []string{
			"divisão por zero", " --> 3:11", "3 |   print(a / 0);"}},
		{"texto nao terminado", "let s = \"abc\n", []string{"erro[sintaxe]: texto não terminado", " --> 1:9"}},
		{"return no nivel superior", "return 1\n", []string{"erro[execução]: 'return' fora de função"}},
		{"entrada termina no meio de um bloco", "fn f() {\n  let a = ;\n", []string{"erro[sintaxe]"}},
		{"fmt com erro", ":fmt let = 1\n", []string{"erro[sintaxe]: esperado 'IDENT', encontrado '='"}},
		{"asm com erro de compilacao", ":asm x\n", []string{"erro[compilação]: variável 'x' não declarada"}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			got := sessao(t, c.entrada)
			for _, q := range c.quer {
				if !strings.Contains(got, q) {
					t.Errorf("saída deveria conter %q:\n%s", q, got)
				}
			}
		})
	}
}

func TestRecuperaDepoisDeErro(t *testing.T) {
	got := sessao(t, "let x = 10\nx / 0\nx + 1\n")
	if !strings.Contains(got, "divisão por zero") || !strings.HasSuffix(got, ">> 11\n>> ") {
		t.Errorf("a sessão deveria continuar após o erro:\n%s", got)
	}
}

func TestIncompleta(t *testing.T) {
	casos := []struct {
		fonte string
		quer  bool
	}{
		{"", false}, {"1 + 2", false}, {"fn f() {", true}, {"fn f() { }", false}, {"[1,", true},
		{"f(1,", true}, {"}", false}, {"{ ( }", true}, {"let s = \"{\";", false}, {"// {", false},
	}
	for _, c := range casos {
		if got := Incompleta(c.fonte); got != c.quer {
			t.Errorf("Incompleta(%q) = %v, quer %v", c.fonte, got, c.quer)
		}
	}
}

func TestSessaoAvaliar(t *testing.T) {
	var saida strings.Builder
	s := NovaSessao(&saida)
	v, diag := s.Avaliar("let x = 2")
	if v != "" || diag != "" {
		t.Errorf("let: %q %q", v, diag)
	}
	if v, diag = s.Avaliar("x * 21"); v != "42" || diag != "" {
		t.Errorf("x * 21: %q %q", v, diag)
	}
	if v, diag = s.Avaliar("print(x)"); v != "" || diag != "" || saida.String() != "2\n" {
		t.Errorf("print: %q %q saída %q", v, diag, saida.String())
	}
	if _, diag = s.Avaliar("y"); !strings.Contains(diag, "variável 'y' não declarada") {
		t.Errorf("diagnóstico = %q", diag)
	}
}

func TestAsm(t *testing.T) {
	got := sessao(t, ":asm 1 + 2\n")
	for _, q := range []string{"== principal (aridade 0, vars 0) ==", "CONST", "; 1", "; 2", "SOMA", "RETORNAR"} {
		if !strings.Contains(got, q) {
			t.Errorf("listagem deveria conter %q:\n%s", q, got)
		}
	}
}
