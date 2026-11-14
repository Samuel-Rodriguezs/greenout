package tipos

import (
	"reflect"
	"testing"

	"greenout/comp/ast"
	"greenout/comp/parser"
	"greenout/comp/visitor"
)

func verificar(t *testing.T, fonte string) (*ast.Programa, *Resultado) {
	t.Helper()
	prog, erros := parser.Analisar(fonte)
	if len(erros) > 0 {
		t.Fatalf("erro de sintaxe: %v", erros)
	}
	return prog, Verificar(prog, Opcoes{Embutidos: PadraoEmbutidos()})
}

func TestProgramasValidos(t *testing.T) {
	casos := []struct{ nome, fonte string }{
		{"aritmetica", "let a = 1 + 2 * 3 - 4 / 2 % 3; print(a);"},
		{"texto", `let s = "a" + "b"; print(s, len(s), s[0]);`},
		{"booleanos", "let b = (1 < 2) && !(3 == 4) || false; if (b) { print(1); }"},
		{"parametros dinamicos", "fn soma(a, b) { return a + b; } print(soma(1, 2), soma(\"a\", \"b\"));"},
		{"recursao", "fn fat(n) { if (n <= 1) { return 1; } return n * fat(n - 1); } let x = fat(5) + 1;"},
		{"arrays", "let a = [1, \"x\", true]; a[0] = 9; push(a, 2); print(a[1], len(a));"},
		{"closure", "fn mk(n) { return fn(x) { return x + n; }; } let f = mk(1); print(f(2));"},
		{"let com funcao", "let f = fn(n) { if (n == 0) { return 0; } return f(n - 1); }; print(f(3));"},
		{"while", "let i = 0; while (i < 10) { i = i + 1; }"},
		{"comparar texto", `print("a" < "b", "a" == "a");`},
		{"atribuir resultado desconhecido", "fn f(x) { return x; } let n = 1; n = f(2);"},
		{"funcao sem retorno usada como valor", "fn f() { } let x = f(); print(x);"},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			_, r := verificar(t, c.fonte)
			if len(r.Erros) > 0 {
				t.Errorf("erros inesperados: %v", r.Mensagens())
			}
		})
	}
}

func TestErros(t *testing.T) {
	casos := []struct {
		nome  string
		fonte string
		quer  []string
	}{
		{"soma int e texto", `let x = 1 + "a";`, []string{"1:11: operador '+' requer dois int ou dois texto, recebeu int e texto"}},
		{"subtracao de texto", `let x = "a" - 1;`, []string{"1:13: operador '-' requer int, recebeu texto e int"}},
		{"soma de bool", "let x = true + false;", []string{"1:14: operador '+' requer dois int ou dois texto, recebeu bool e bool"}},
		{"comparar tipos distintos", `let x = 1 == "a";`, []string{"1:11: comparação entre tipos incompatíveis: int e texto"}},
		{"ordenar bool", "let x = true < false;", []string{"1:14: operador '<' requer dois int ou dois texto, recebeu bool e bool"}},
		{"ordenar int e texto", `let x = 1 < "a";`, []string{"1:11: operador '<' requer dois int ou dois texto, recebeu int e texto"}},
		{"e com int", "let x = 1 && true;", []string{"1:11: operador '&&' requer bool, recebeu int e bool"}},
		{"negacao de int", "let x = !1;", []string{"1:9: operador '!' requer bool, recebeu int"}},
		{"menos de texto", `let x = -"a";`, []string{"1:9: operador '-' requer int, recebeu texto"}},
		{"if com int", "if (1) { }", []string{"1:5: condição deve ser bool, recebeu int"}},
		{"while com texto", `while ("a") { }`, []string{"1:8: condição deve ser bool, recebeu texto"}},
		{"atribuicao de tipo errado", "let x = 1;\nx = \"s\";", []string{"2:3: não é possível atribuir texto à variável 'x' do tipo int"}},
		{"indice nao int", "let a = [1];\nprint(a[\"0\"]);", []string{"2:9: índice deve ser int, recebeu texto"}},
		{"indexar int", "let n = 1;\nprint(n[0]);", []string{"2:8: indexação requer array ou texto, recebeu int"}},
		{"atribuir indice de texto", "let s = \"abc\";\ns[0] = \"x\";", []string{"2:2: texto não permite atribuição por índice"}},
		{"atribuir indice de int", "let n = 1;\nn[0] = 1;", []string{"2:2: indexação requer array, recebeu int"}},
		{"aridade", "fn f(a, b) { return a; }\nf(1);", []string{"2:2: 'f' espera 2 argumento(s), recebeu 1"}},
		{"aridade de embutido", "len(1, 2);", []string{"1:4: 'len' espera 1 argumento(s), recebeu 2"}},
		{"tipo de argumento", "push(1, 2);", []string{"1:6: argumento 1 de 'push' deveria ser array, recebeu int"}},
		{"chamar nao funcao", "let n = 1;\nn(2);", []string{"2:2: valor do tipo int não é chamável"}},
		{"aridade via variavel", "let f = fn(a) { return a; };\nf(1, 2);", []string{"2:2: 'f' espera 1 argumento(s), recebeu 2"}},
		{"retorno inferido", "fn f() { return 1; }\nlet s = f() + \"a\";", []string{"2:13: operador '+' requer dois int ou dois texto, recebeu int e texto"}},
		{"retorno inferido de texto", "fn f() { return \"a\"; }\nlet n = f() * 2;", []string{"2:13: operador '*' requer int, recebeu texto e int"}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			_, r := verificar(t, c.fonte)
			if got := r.Mensagens(); !reflect.DeepEqual(got, c.quer) {
				t.Errorf("erros = %q\nquer   %q", got, c.quer)
			}
		})
	}
}

// tipoDe devolve o tipo inferido da última expressão que satisfaz o predicado
// (a última, para ignorar chamadas recursivas dentro do corpo).
func tipoDe(t *testing.T, fonte string, escolher func(ast.No) bool) Base {
	t.Helper()
	prog, r := verificar(t, fonte)
	var achado ast.Expressao
	visitor.Inspecionar(prog, func(n ast.No) bool {
		if e, ok := n.(ast.Expressao); ok && escolher(n) {
			achado = e
		}
		return true
	})
	if achado == nil {
		t.Fatal("expressão não encontrada")
	}
	return r.Tipos[achado]
}

func TestInferenciaDeRetorno(t *testing.T) {
	ehChamadaDeF := func(n ast.No) bool {
		c, ok := n.(*ast.Chamada)
		if !ok {
			return false
		}
		id, ok := c.Funcao.(*ast.Identificador)
		return ok && id.Nome == "f"
	}
	casos := []struct {
		nome  string
		fonte string
		quer  Base
	}{
		{"int", "fn f() { return 1; } f();", Int},
		{"texto", `fn f() { return "a"; } f();`, Texto},
		{"sem return", "fn f() { } f();", Nulo},
		{"return vazio", "fn f() { return; } f();", Nulo},
		{"tipos diferentes", `fn f(x) { if (x) { return 1; } return "a"; } f(true);`, Qualquer},
		{"pode cair no fim", "fn f(x) { if (x) { return 1; } } f(true);", Qualquer},
		{"if else ambos retornam", "fn f(x) { if (x) { return 1; } else { return 2; } } f(true);", Int},
		{"recursao", "fn f(n) { if (n == 0) { return 0; } return n * f(n - 1); } f(3);", Int},
		{"parametro", "fn f(x) { return x; } f(1);", Qualquer},
		{"funcao anonima em let", "let f = fn() { return true; }; f();", Bool},
		{"embutido len", "let f = len; f([1]);", Int},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := tipoDe(t, c.fonte, ehChamadaDeF); got != c.quer {
				t.Errorf("tipo = %s, quer %s", got, c.quer)
			}
		})
	}
}

func TestTiposDeExpressoes(t *testing.T) {
	casos := []struct {
		fonte string
		quer  Base
	}{
		{"1 + 2;", Int}, {`"a" + "b";`, Texto}, {"1 < 2;", Bool}, {"[1, 2];", Array},
		{"fn() { };", Func}, {"!true;", Bool}, {"-1;", Int}, {"len([1]);", Int},
		{`"abc"[0];`, Texto}, {"[1][0];", Qualquer},
	}
	for _, c := range casos {
		prog, r := verificar(t, c.fonte)
		e := prog.Comandos[0].(*ast.ComandoExpr).Expr
		if got := r.Tipos[e]; got != c.quer {
			t.Errorf("%s: tipo = %s, quer %s", c.fonte, got, c.quer)
		}
	}
}

func TestSemEmbutidosEIndefinidos(t *testing.T) {
	prog, _ := parser.Analisar("print(naoexiste + 1);")
	r := Verificar(prog, Opcoes{})
	if len(r.Erros) != 0 {
		t.Errorf("nomes indefinidos são tarefa da semântica: %v", r.Mensagens())
	}
}

func TestCompativelEString(t *testing.T) {
	if !Compativel(Int, Qualquer) || !Compativel(Qualquer, Bool) || Compativel(Int, Texto) || !Compativel(Int, Int) {
		t.Error("Compativel incorreto")
	}
	if s := PadraoEmbutidos()["push"].String(); s != "fn(array, qualquer) -> array" {
		t.Errorf("String() = %q", s)
	}
}
