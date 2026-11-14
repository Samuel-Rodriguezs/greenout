package interp

import (
	"fmt"
	"strings"
	"testing"

	"greenout/comp/parser"
)

// novoComPrint cria um interpretador com um print que escreve em sb.
func novoComPrint(sb *strings.Builder) *Interp {
	in := Novo()
	in.DefinirEmbutido("print", &Nativa{Nome: "print", Aridade: -1, Fn: func(args []Valor) (Valor, error) {
		partes := make([]string, len(args))
		for i, a := range args {
			partes[i] = a.String()
		}
		sb.WriteString(strings.Join(partes, " ") + "\n")
		return Nulo{}, nil
	}})
	in.DefinirEmbutido("len", &Nativa{Nome: "len", Aridade: 1, Fn: func(args []Valor) (Valor, error) {
		switch x := args[0].(type) {
		case Texto:
			return Inteiro(len(x)), nil
		case *Array:
			return Inteiro(len(x.Elems)), nil
		}
		return nil, fmt.Errorf("len não aplicável a %s", args[0].Tipo())
	}})
	in.DefinirEmbutido("push", &Nativa{Nome: "push", Aridade: 2, Fn: func(args []Valor) (Valor, error) {
		a, ok := args[0].(*Array)
		if !ok {
			return nil, fmt.Errorf("push requer array")
		}
		a.Elems = append(a.Elems, args[1])
		return a, nil
	}})
	return in
}

func rodar(t *testing.T, fonte string) (string, error) {
	t.Helper()
	prog, erros := parser.Analisar(fonte)
	if len(erros) > 0 {
		t.Fatalf("erro de sintaxe: %v", erros)
	}
	var sb strings.Builder
	_, err := novoComPrint(&sb).Executar(prog)
	return sb.String(), err
}

func TestProgramas(t *testing.T) {
	casos := []struct {
		nome  string
		fonte string
		quer  string
	}{
		{"aritmetica", "print(1 + 2 * 3, (1 + 2) * 3, 10 / 3, 10 % 3, -4 + 1);", "7 9 3 1 -3\n"},
		{"divisao negativa", "print(-7 / 2, -7 % 3);", "-3 -1\n"},
		{"texto", `print("ab" + "cd", len("abc"), "abc"[1], "a" < "b");`, "abcd 3 b true\n"},
		{"booleanos", "print(true && false, true || false, !true, 1 < 2, 2 <= 2, 3 > 4, 3 >= 3);", "false true false true true false true\n"},
		{"igualdade", `print(1 == 1, 1 == "1", "a" == "a", true != false, [1, 2] == [1, 2], [1] == [2]);`, "true false true true true false\n"},
		{"curto circuito", "fn boom() { print(\"chamou\"); return true; } print(false && boom(), true || boom());", "false true\n"},
		{"avaliacao do lado direito", "fn boom() { print(\"chamou\"); return true; } print(true && boom());", "chamou\ntrue\n"},
		{"variaveis e atribuicao", "let x = 1; x = x + 1; print(x);", "2\n"},
		{"if else", "let x = 5; if (x > 3) { print(\"grande\"); } else { print(\"pequeno\"); }", "grande\n"},
		{"else if", "fn f(n) { if (n < 0) { return \"neg\"; } else if (n == 0) { return \"zero\"; } else { return \"pos\"; } } print(f(-1), f(0), f(1));", "neg zero pos\n"},
		{"while", "let i = 0; let s = 0; while (i < 5) { s = s + i; i = i + 1; } print(s);", "10\n"},
		{"fatorial", "fn fat(n) { if (n <= 1) { return 1; } return n * fat(n - 1); } print(fat(10));", "3628800\n"},
		{"fibonacci", "fn fib(n) { if (n < 2) { return n; } return fib(n - 1) + fib(n - 2); } print(fib(15));", "610\n"},
		{"recursao mutua com hoisting", "print(par(10)); fn par(n) { if (n == 0) { return true; } return impar(n - 1); } fn impar(n) { if (n == 0) { return false; } return par(n - 1); }", "true\n"},
		{"funcao sem return", "fn f() { } print(f());", "nulo\n"},
		{"return vazio", "fn f() { return; } print(f());", "nulo\n"},
		{"return dentro de while", "fn f() { let i = 0; while (true) { if (i == 3) { return i; } i = i + 1; } } print(f());", "3\n"},
		{"closure contador", "fn mk() { let c = 0; return fn() { c = c + 1; return c; }; } let a = mk(); let b = mk(); print(a(), a(), b(), a());", "1 2 1 3\n"},
		{"closure captura parametro", "fn soma(n) { return fn(x) { return x + n; }; } let s5 = soma(5); print(s5(1), soma(10)(1));", "6 11\n"},
		{"funcao de ordem superior", "fn aplica(f, x) { return f(f(x)); } print(aplica(fn(n) { return n * 2; }, 3));", "12\n"},
		{"closure por iteracao", "let fs = []; let i = 0; while (i < 3) { let j = i; push(fs, fn() { return j; }); i = i + 1; } print(fs[0](), fs[1](), fs[2]());", "0 1 2\n"},
		{"let com funcao recursiva", "let f = fn(n) { if (n == 0) { return 0; } return n + f(n - 1); }; print(f(4));", "10\n"},
		{"sombreamento", "let x = 1; { let x = 2; print(x); } print(x);", "2\n1\n"},
		{"let usa externo", "let x = 1; { let x = x + 10; print(x); } print(x);", "11\n1\n"},
		{"atribuicao ao externo", "let x = 1; { x = 5; } print(x);", "5\n"},
		{"arrays", "let a = [1, 2, 3]; a[1] = 20; push(a, 4); print(a, len(a), a[3]);", "[1, 20, 3, 4] 4 4\n"},
		{"arrays aninhados e texto", `let m = [[1, 2], ["a"]]; m[0][1] = 9; print(m);`, "[[1, 9], [\"a\"]]\n"},
		{"arrays por referencia", "let a = [1]; let b = a; b[0] = 7; print(a[0]);", "7\n"},
		{"funcao como valor", "fn f() { return 1; } let g = f; print(g(), f == g);", "1 true\n"},
		{"comentarios", "// nada\nlet a = 1; // aqui\nprint(a);", "1\n"},
		{"estouro com wrap", "print(9223372036854775807 + 1);", "-9223372036854775808\n"},
		{"representacao de funcoes", "fn f() {} let g = fn() {}; print(f, g, len);", "<função f> <função g> <embutido len>\n"},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			got, err := rodar(t, c.fonte)
			if err != nil {
				t.Fatalf("erro: %v", err)
			}
			if got != c.quer {
				t.Errorf("saída = %q, quer %q", got, c.quer)
			}
		})
	}
}

func TestErrosDeExecucao(t *testing.T) {
	casos := []struct {
		nome  string
		fonte string
		quer  string
	}{
		{"variavel indefinida", "print(x);", "1:7: variável 'x' não declarada"},
		{"atribuir indefinida", "x = 1;", "1:1: variável 'x' não declarada"},
		{"divisao por zero", "let a = 1;\nprint(a / 0);", "2:9: divisão por zero"},
		{"resto por zero", "print(5 % 0);", "1:9: divisão por zero"},
		{"soma de tipos", `print(1 + "a");`, "1:9: operador '+' não aplicável a int e texto"},
		{"menos de texto", `print(-"a");`, "1:7: operador '-' não aplicável a texto"},
		{"nao de int", "print(!1);", "1:7: operador '!' não aplicável a int"},
		{"condicao nao bool", "if (1) { }", "1:5: esperado bool, recebeu int"},
		{"while nao bool", "while (\"x\") { }", "1:8: esperado bool, recebeu texto"},
		{"logico nao bool", "print(1 && true);", "1:9: esperado bool, recebeu int"},
		{"logico direito nao bool", "print(true && 1);", "1:12: esperado bool, recebeu int"},
		{"indice fora", "let a = [1, 2];\nprint(a[2]);", "2:8: índice 2 fora dos limites (tamanho 2)"},
		{"indice negativo", "let a = [1];\nprint(a[0 - 1]);", "2:8: índice -1 fora dos limites (tamanho 1)"},
		{"indice de texto fora", `print("ab"[5]);`, "1:11: índice 5 fora dos limites (tamanho 2)"},
		{"indice nao int", `print([1]["a"]);`, "1:10: índice deve ser int, recebeu texto"},
		{"indexar int", "print(1[0]);", "1:8: indexação requer array ou texto, recebeu int"},
		{"atribuir indice fora", "let a = [];\na[0] = 1;", "2:2: índice 0 fora dos limites (tamanho 0)"},
		{"atribuir indice de texto", "let s = \"ab\";\ns[0] = \"x\";", "2:2: atribuição por índice requer array, recebeu texto"},
		{"chamar nao funcao", "let n = 1;\nn();", "2:2: valor do tipo int não é chamável"},
		{"aridade", "fn f(a, b) { return a; }\nf(1);", "2:2: 'f' espera 2 argumento(s), recebeu 1"},
		{"aridade anonima", "let g = fn(a) { };\n(fn(a) { })(1, 2);", "2:12: função espera 1 argumento(s), recebeu 2"},
		{"aridade de embutido", "len(1, 2);", "1:4: 'len' espera 1 argumento(s), recebeu 2"},
		{"erro de embutido recebe posicao", "len(1);", "1:4: len não aplicável a int"},
		{"estouro de pilha", "fn f(n) { return f(n + 1); }\nf(0);", "1:19: estouro de pilha: recursão profunda demais"},
		{"return no nivel superior", "return 1;", "1:1: 'return' fora de função"},
		{"erro dentro de funcao", "fn f(x) {\n  return x / 0;\n}\nprint(f(1));", "2:12: divisão por zero"},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			_, err := rodar(t, c.fonte)
			if err == nil {
				t.Fatalf("esperado erro %q", c.quer)
			}
			if err.Error() != c.quer {
				t.Errorf("erro = %q, quer %q", err.Error(), c.quer)
			}
		})
	}
}

func TestEstadoPersisteEntreExecucoes(t *testing.T) {
	var sb strings.Builder
	in := novoComPrint(&sb)
	passos := []struct {
		fonte string
		quer  string // String() do valor devolvido
	}{
		{"let x = 10;", "nulo"},
		{"fn dobro(n) { return n * 2; }", "nulo"},
		{"x + 1;", "11"},
		{"dobro(x);", "20"},
		{"x = 3; x;", "3"},
		{`"a" + "b";`, "ab"},
	}
	for _, p := range passos {
		prog, erros := parser.Analisar(p.fonte)
		if len(erros) > 0 {
			t.Fatal(erros)
		}
		v, err := in.Executar(prog)
		if err != nil {
			t.Fatalf("%q: %v", p.fonte, err)
		}
		if v.String() != p.quer {
			t.Errorf("%q = %s, quer %s", p.fonte, v, p.quer)
		}
	}
	if _, ok := in.Global().Buscar("x"); !ok {
		t.Error("x deveria estar no ambiente global")
	}
	// depois de um erro, o estado anterior continua válido
	prog, _ := parser.Analisar("x / 0;")
	if _, err := in.Executar(prog); err == nil {
		t.Fatal("esperado erro")
	}
	prog, _ = parser.Analisar("x;")
	if v, err := in.Executar(prog); err != nil || v.String() != "3" {
		t.Errorf("após erro: %v %v", v, err)
	}
}

func TestEnv(t *testing.T) {
	pai := NovoEnv(nil)
	pai.Definir("a", Inteiro(1))
	filho := NovoEnv(pai)
	filho.Definir("b", Inteiro(2))
	if v, ok := filho.Buscar("a"); !ok || v != Inteiro(1) {
		t.Errorf("Buscar(a) = %v %v", v, ok)
	}
	if _, ok := pai.Buscar("b"); ok {
		t.Error("pai não enxerga filho")
	}
	if !filho.Atribuir("a", Inteiro(9)) {
		t.Error("Atribuir(a) deveria funcionar")
	}
	if v, _ := pai.Buscar("a"); v != Inteiro(9) {
		t.Errorf("a no pai = %v", v)
	}
	if filho.Atribuir("zzz", Inteiro(0)) {
		t.Error("Atribuir de inexistente deveria falhar")
	}
}

func TestOperacoesDeValor(t *testing.T) {
	casos := []struct {
		op   string
		a, b Valor
		quer string
		erro bool
	}{
		{"+", Inteiro(2), Inteiro(3), "5", false},
		{"*", Inteiro(-2), Inteiro(3), "-6", false},
		{"+", Texto("a"), Texto("b"), "ab", false},
		{"<", Texto("a"), Texto("b"), "true", false},
		{">=", Inteiro(1), Inteiro(2), "false", false},
		{"==", Nulo{}, Nulo{}, "true", false},
		{"==", Inteiro(1), Booleano(true), "false", false},
		{"+", Inteiro(1), Texto("a"), "", true},
		{"<", Booleano(true), Booleano(false), "", true},
		{"/", Inteiro(1), Inteiro(0), "", true},
	}
	for _, c := range casos {
		v, err := Operar(c.op, c.a, c.b)
		if (err != nil) != c.erro {
			t.Errorf("%v %s %v: erro = %v", c.a, c.op, c.b, err)
			continue
		}
		if err == nil && v.String() != c.quer {
			t.Errorf("%v %s %v = %v, quer %s", c.a, c.op, c.b, v, c.quer)
		}
	}
}

func TestRepr(t *testing.T) {
	a := &Array{Elems: []Valor{Inteiro(1), Texto("x"), &Array{Elems: []Valor{Booleano(true), Nulo{}}}}}
	if got := Repr(a); got != `[1, "x", [true, nulo]]` {
		t.Errorf("Repr = %s", got)
	}
	if Texto("x").String() != "x" || Repr(Texto("x")) != `"x"` {
		t.Error("String/Repr de texto")
	}
	ciclo := &Array{}
	ciclo.Elems = []Valor{ciclo}
	if s := ciclo.String(); !strings.Contains(s, "[...]") {
		t.Errorf("ciclo deveria ser truncado: %s", s)
	}
}
