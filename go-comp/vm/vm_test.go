package vm

import (
	"fmt"
	"strings"
	"testing"

	"greenout/comp/codigo"
	"greenout/comp/compilador"
	"greenout/comp/interp"
	"greenout/comp/parser"
	"greenout/comp/token"
)

func nativas(sb *strings.Builder) map[string]*interp.Nativa {
	return map[string]*interp.Nativa{
		"print": {Nome: "print", Aridade: -1, Fn: func(args []interp.Valor) (interp.Valor, error) {
			partes := make([]string, len(args))
			for i, a := range args {
				partes[i] = a.String()
			}
			sb.WriteString(strings.Join(partes, " ") + "\n")
			return interp.Nulo{}, nil
		}},
		"len": {Nome: "len", Aridade: 1, Fn: func(args []interp.Valor) (interp.Valor, error) {
			switch x := args[0].(type) {
			case interp.Texto:
				return interp.Inteiro(len(x)), nil
			case *interp.Array:
				return interp.Inteiro(len(x.Elems)), nil
			}
			return nil, fmt.Errorf("len não aplicável a %s", args[0].Tipo())
		}},
		"push": {Nome: "push", Aridade: 2, Fn: func(args []interp.Valor) (interp.Valor, error) {
			a, ok := args[0].(*interp.Array)
			if !ok {
				return nil, fmt.Errorf("push requer array")
			}
			a.Elems = append(a.Elems, args[1])
			return a, nil
		}},
	}
}

func nomes(m map[string]*interp.Nativa) []string {
	var ns []string
	for n := range m {
		ns = append(ns, n)
	}
	return ns
}

func rodar(t *testing.T, fonte string) (string, error) {
	t.Helper()
	prog, erros := parser.Analisar(fonte)
	if len(erros) > 0 {
		t.Fatalf("erro de sintaxe: %v", erros)
	}
	var sb strings.Builder
	nat := nativas(&sb)
	p, err := compilador.Compilar(prog, nomes(nat))
	if err != nil {
		t.Fatalf("erro de compilação: %v", err)
	}
	m := Novo(p, nat)
	err = m.Executar()
	if err == nil && len(m.pilha) != 0 {
		t.Errorf("pilha deveria terminar vazia, tem %d valores", len(m.pilha))
	}
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
		{"closures aninhadas em varios niveis", "fn a(x) { return fn(y) { return fn(z) { return x + y + z; }; }; } print(a(1)(10)(100));", "111\n"},
		{"let com funcao recursiva", "let f = fn(n) { if (n == 0) { return 0; } return n + f(n - 1); }; print(f(4));", "10\n"},
		{"sombreamento", "let x = 1; { let x = 2; print(x); } print(x);", "2\n1\n"},
		{"let usa externo", "let x = 1; { let x = x + 10; print(x); } print(x);", "11\n1\n"},
		{"atribuicao ao externo", "let x = 1; { x = 5; } print(x);", "5\n"},
		{"arrays", "let a = [1, 2, 3]; a[1] = 20; push(a, 4); print(a, len(a), a[3]);", "[1, 20, 3, 4] 4 4\n"},
		{"arrays aninhados e texto", `let m = [[1, 2], ["a"]]; m[0][1] = 9; print(m);`, "[[1, 9], [\"a\"]]\n"},
		{"arrays por referencia", "let a = [1]; let b = a; b[0] = 7; print(a[0]);", "7\n"},
		{"funcao como valor", "fn f() { return 1; } let g = f; print(g(), f == g);", "1 true\n"},
		{"estouro com wrap", "print(9223372036854775807 + 1);", "-9223372036854775808\n"},
		{"representacao de funcoes", "fn f() {} let g = fn() {}; print(f, g, len);", "<função f> <função g> <embutido len>\n"},
		{"argumentos na ordem", "fn f(a, b, c) { return a * 100 + b * 10 + c; } print(f(1, 2, 3));", "123\n"},
		{"expressao com chamadas aninhadas na pilha", "fn d(x) { return x * 2; } print(1 + d(2) + d(d(3)) * 2);", "29\n"},
		{"laco que retorna no meio de expressao", "fn f(n) { let i = 0; while (i < 10) { if (i == n) { return i * 10; } i = i + 1; } return 0 - 1; } print(1 + f(3), f(20));", "31 -1\n"},
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

// Os erros da VM devem ter exatamente a mesma mensagem e posição do interpretador.
func TestErrosDeExecucao(t *testing.T) {
	casos := []struct {
		nome  string
		fonte string
		quer  string
	}{
		{"divisao por zero", "let a = 1;\nprint(a / 0);", "2:9: divisão por zero"},
		{"resto por zero", "print(5 % 0);", "1:9: divisão por zero"},
		{"soma de tipos", `print(1 + "a");`, "1:9: operador '+' não aplicável a int e texto"},
		{"menos de texto", `print(-"a");`, "1:7: operador '-' não aplicável a texto"},
		{"nao de int", "print(!1);", "1:7: operador '!' não aplicável a int"},
		{"condicao nao bool", "if (1) { }", "1:5: esperado bool, recebeu int"},
		{"while nao bool", "while (\"x\") { }", "1:8: esperado bool, recebeu texto"},
		{"logico nao bool", "print(1 && true);", "1:9: esperado bool, recebeu int"},
		{"logico direito nao bool", "print(true && 1);", "1:12: esperado bool, recebeu int"},
		{"ou nao bool", "print(0 || true);", "1:9: esperado bool, recebeu int"},
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
		{"funcao anonima devolvida nao herda nome", "fn mk() { return fn(a) { }; }\nlet g = mk();\ng(1, 2);", "3:2: função espera 1 argumento(s), recebeu 2"},
		{"aridade de embutido", "len(1, 2);", "1:4: 'len' espera 1 argumento(s), recebeu 2"},
		{"erro de embutido recebe posicao", "len(1);", "1:4: len não aplicável a int"},
		{"estouro de pilha", "fn f(n) { return f(n + 1); }\nf(0);", "1:19: estouro de pilha: recursão profunda demais"},
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

func TestRecursaoProfundaDentroDoLimite(t *testing.T) {
	got, err := rodar(t, "fn soma(n) { if (n == 0) { return 0; } return n + soma(n - 1); } print(soma(4000));")
	if err != nil || got != "8002000\n" {
		t.Errorf("got %q err %v", got, err)
	}
}

func TestEmbutidoIndisponivel(t *testing.T) {
	prog, _ := parser.Analisar("sumiu(1);")
	p, err := compilador.Compilar(prog, []string{"sumiu"})
	if err != nil {
		t.Fatal(err)
	}
	err = Novo(p, map[string]*interp.Nativa{}).Executar()
	if err == nil || err.Error() != "1:1: embutido 'sumiu' indisponível" {
		t.Errorf("erro = %v", err)
	}
}

func TestVariavelNaoInicializada(t *testing.T) {
	// bytecode escrito à mão: lê a posição 0 antes de qualquer GUARDAR
	main := &codigo.Funcao{Nome: "principal", NumVars: 1}
	pos := token.Posicao{Linha: 1, Coluna: 1}
	main.Emitir(codigo.OpCarregar, 0, 0, pos)
	main.Emitir(codigo.OpPop, 0, 0, pos)
	main.Emitir(codigo.OpNulo, 0, 0, pos)
	main.Emitir(codigo.OpRetornar, 0, 0, pos)
	err := Novo(&codigo.Programa{Principal: main}, nil).Executar()
	if err == nil || !strings.Contains(err.Error(), "antes de ser inicializada") {
		t.Errorf("erro = %v", err)
	}
}

func TestOpcodeDesconhecido(t *testing.T) {
	main := &codigo.Funcao{Nome: "principal"}
	main.Emitir(codigo.Opcode(200), 0, 0, token.Posicao{Linha: 3, Coluna: 4})
	err := Novo(&codigo.Programa{Principal: main}, nil).Executar()
	if err == nil || err.Error() != "3:4: opcode desconhecido OP(200)" {
		t.Errorf("erro = %v", err)
	}
}

func TestVMReutilizavel(t *testing.T) {
	prog, _ := parser.Analisar("let i = 0; while (i < 3) { i = i + 1; } print(i);")
	var sb strings.Builder
	nat := nativas(&sb)
	p, err := compilador.Compilar(prog, nomes(nat))
	if err != nil {
		t.Fatal(err)
	}
	m := Novo(p, nat)
	for i := 0; i < 3; i++ {
		if err := m.Executar(); err != nil {
			t.Fatal(err)
		}
	}
	if sb.String() != "3\n3\n3\n" {
		t.Errorf("saída = %q", sb.String())
	}
}

func TestFechoString(t *testing.T) {
	if s := (&Fecho{Fn: &codigo.Funcao{Nome: "f"}}).String(); s != "<função f>" {
		t.Errorf("String = %q", s)
	}
	if s := (&Fecho{Fn: &codigo.Funcao{}}).String(); s != "<função>" {
		t.Errorf("String = %q", s)
	}
}
