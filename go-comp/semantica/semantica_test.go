package semantica

import (
	"reflect"
	"testing"

	"greenout/comp/parser"
)

var embutidos = Opcoes{Embutidos: []string{"print", "len", "push"}}

func analisar(t *testing.T, fonte string) *Resultado {
	t.Helper()
	prog, erros := parser.Analisar(fonte)
	if len(erros) > 0 {
		t.Fatalf("erro de sintaxe: %v", erros)
	}
	return Analisar(prog, embutidos)
}

func TestProgramasValidos(t *testing.T) {
	casos := []struct{ nome, fonte string }{
		{"variaveis", "let a = 1; let b = a + 2; print(b);"},
		{"recursao", "fn fat(n) { if (n <= 1) { return 1; } return n * fat(n - 1); } print(fat(5));"},
		{"recursao mutua", "fn par(n) { if (n == 0) { return true; } return impar(n - 1); } fn impar(n) { if (n == 0) { return false; } return par(n - 1); } print(par(4));"},
		{"closure", "fn cont() { let c = 0; return fn() { c = c + 1; return c; }; } let f = cont(); print(f());"},
		{"let com funcao recursiva", "let f = fn(n) { if (n == 0) { return 0; } return f(n - 1); }; print(f(3));"},
		{"sombreamento", "let x = 1; { let x = 2; print(x); } print(x);"},
		{"parametro sombreia", "let x = 1; fn f(x) { return x; } print(f(2), x);"},
		{"let usa valor externo com mesmo nome", "let x = 1; { let x = x + 1; print(x); }"},
		{"arrays", "let a = [1, 2]; a[0] = 5; push(a, 3); print(len(a), a[1]);"},
		{"sombrear embutido", "let len = 3; print(len);"},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			r := analisar(t, c.fonte)
			if len(r.Erros) > 0 {
				t.Errorf("erros inesperados: %v", r.Mensagens())
			}
			if len(r.Avisos) > 0 {
				t.Errorf("avisos inesperados: %v", r.Avisos)
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
		{"nao declarada", "print(x);", []string{"1:7: variável 'x' não declarada"}},
		{"uso antes da declaracao", "print(a);\nlet a = 1;", []string{"1:7: variável 'a' não declarada"}},
		{"let usa a si mesmo", "let a = a + 1;", []string{"1:9: variável 'a' não declarada"}},
		{"redeclaracao", "let a = 1;\nlet a = 2;", []string{"2:5: 'a' já declarado neste escopo (declaração anterior em 1:5)"}},
		{"funcao redeclarada", "fn f() {}\nfn f() {}", []string{"2:4: 'f' já declarado neste escopo (declaração anterior em 1:4)"}},
		{"let conflita com funcao", "fn f() {}\nlet f = 1;", []string{"2:5: 'f' já declarado neste escopo (declaração anterior em 1:4)"}},
		{"redeclaracao do parametro no corpo", "fn f(a) { let a = 1; return a; }", []string{"1:15: 'a' já declarado neste escopo (declaração anterior em 1:6)"}},
		{"parametro duplicado", "fn f(a, a) { return a; }", []string{"1:9: parâmetro 'a' duplicado"}},
		{"return fora de funcao", "return 1;", []string{"1:1: 'return' fora de função"}},
		{"return em bloco global", "if (true) { return; }", []string{"1:13: 'return' fora de função"}},
		{"atribuicao nao declarada", "x = 1;", []string{"1:1: atribuição a variável não declarada 'x'"}},
		{"atribuicao a funcao", "fn f() {}\nf = 1;", []string{"2:1: não é possível atribuir a função 'f'"}},
		{"atribuicao a embutido", "len = 1;", []string{"1:1: não é possível atribuir a embutido 'len'"}},
		{"variavel de bloco fora do bloco", "{ let a = 1; print(a); }\nprint(a);", []string{"2:7: variável 'a' não declarada"}},
		{"variavel local da funcao", "fn f() { let a = 1; return a; }\nprint(a);", []string{"2:7: variável 'a' não declarada"}},
		{"alvo de indice invalido", "a[0] = 1;", []string{"1:1: variável 'a' não declarada"}},
		{"varios erros", "print(a); print(b);", []string{"1:7: variável 'a' não declarada", "1:17: variável 'b' não declarada"}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			r := analisar(t, c.fonte)
			if got := r.Mensagens(); !reflect.DeepEqual(got, c.quer) {
				t.Errorf("erros = %q\nquer   %q", got, c.quer)
			}
		})
	}
}

func TestAvisosNaoUsados(t *testing.T) {
	r := analisar(t, "fn f(p) {\n  let a = 1;\n  let b = 2;\n  return b;\n}\n{ let c = 3; }\nlet global = 1;")
	var got []string
	for _, a := range r.Avisos {
		got = append(got, a.Error())
	}
	quer := []string{"2:7: variável 'a' declarada e não usada", "6:7: variável 'c' declarada e não usada"}
	if !reflect.DeepEqual(got, quer) {
		t.Errorf("avisos = %q, quer %q", got, quer)
	}
	if len(r.Erros) != 0 {
		t.Errorf("erros inesperados: %v", r.Mensagens())
	}
	if r.String() != "0 erro(s), 2 aviso(s)" {
		t.Errorf("String() = %q", r.String())
	}
}

func TestSemEmbutidosDeclarados(t *testing.T) {
	prog, _ := parser.Analisar("print(1);")
	r := Analisar(prog, Opcoes{})
	if len(r.Erros) != 1 {
		t.Errorf("sem embutidos, print deveria ser não declarado: %v", r.Mensagens())
	}
}
