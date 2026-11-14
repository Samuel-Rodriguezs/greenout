package compilador

import (
	"fmt"
	"strings"
	"testing"

	"greenout/comp/codigo"
	"greenout/comp/parser"
)

var embutidos = []string{"print", "len", "push"}

func compilar(t *testing.T, fonte string) *codigo.Programa {
	t.Helper()
	prog, erros := parser.Analisar(fonte)
	if len(erros) > 0 {
		t.Fatalf("erro de sintaxe: %v", erros)
	}
	p, err := Compilar(prog, embutidos)
	if err != nil {
		t.Fatalf("erro de compilação: %v", err)
	}
	if err := p.Validar(); err != nil {
		t.Fatalf("bytecode inválido: %v\n%s", err, codigo.Desmontar(p))
	}
	return p
}

// sequencia resume o código de f como "OP a b; OP; ...".
func sequencia(f *codigo.Funcao) string {
	var partes []string
	for _, ins := range f.Codigo {
		s := ins.Op.String()
		switch ins.Op.Operandos() {
		case 1:
			s += fmt.Sprintf(" %d", ins.A)
		case 2:
			s += fmt.Sprintf(" %d %d", ins.A, ins.B)
		}
		partes = append(partes, s)
	}
	return strings.Join(partes, "; ")
}

func funcaoPorNome(t *testing.T, p *codigo.Programa, nome string) *codigo.Funcao {
	t.Helper()
	for _, f := range p.Funcoes {
		if f.Nome == nome {
			return f
		}
	}
	t.Fatalf("função %q não encontrada", nome)
	return nil
}

func TestSequenciasDeInstrucoes(t *testing.T) {
	casos := []struct {
		nome  string
		fonte string
		quer  string
	}{
		{"let e aritmetica", "let x = 1 + 2 * 3;",
			"CONST 0; CONST 1; CONST 2; MUL; SOMA; GUARDAR 0 0; NULO; RETORNAR"},
		{"constantes repetidas compartilham indice", "let a = 7; let b = 7;",
			"CONST 0; GUARDAR 0 0; CONST 0; GUARDAR 0 1; NULO; RETORNAR"},
		{"booleanos e comparacao", "let b = true; let c = 1 <= 2;",
			"VERDADEIRO; GUARDAR 0 0; CONST 0; CONST 1; MENOR_IGUAL; GUARDAR 0 1; NULO; RETORNAR"},
		{"unarios", "let a = -1; let b = !true;",
			"CONST 0; NEG; GUARDAR 0 0; VERDADEIRO; NAO; GUARDAR 0 1; NULO; RETORNAR"},
		{"expressao como comando", "print(1);",
			"EMBUTIDO 0; CONST 1; CHAMAR 1; POP; NULO; RETORNAR"},
		{"if sem else", "let x = 1; if (x < 2) { print(x); }",
			"CONST 0; GUARDAR 0 0; CARREGAR 0 0; CONST 1; MENOR; SALTO_SE_FALSO 10; " +
				"EMBUTIDO 2; CARREGAR 0 0; CHAMAR 1; POP; NULO; RETORNAR"},
		{"if else", "if (true) { print(1); } else { print(2); }",
			"VERDADEIRO; SALTO_SE_FALSO 7; EMBUTIDO 0; CONST 1; CHAMAR 1; POP; SALTO 11; " +
				"EMBUTIDO 0; CONST 2; CHAMAR 1; POP; NULO; RETORNAR"},
		{"while", "let i = 0; while (i < 3) { i = i + 1; }",
			"CONST 0; GUARDAR 0 0; CARREGAR 0 0; CONST 1; MENOR; SALTO_SE_FALSO 11; " +
				"CARREGAR 0 0; CONST 2; SOMA; GUARDAR 0 0; SALTO 2; NULO; RETORNAR"},
		{"curto circuito e", "let a = true; let b = false; let r = a && b;",
			"VERDADEIRO; GUARDAR 0 0; FALSO; GUARDAR 0 1; CARREGAR 0 0; MANTER_SE_FALSO 8; " +
				"CARREGAR 0 1; EXIGIR_BOOL; GUARDAR 0 2; NULO; RETORNAR"},
		{"curto circuito ou", "let a = true; let b = false; let r = a || b;",
			"VERDADEIRO; GUARDAR 0 0; FALSO; GUARDAR 0 1; CARREGAR 0 0; MANTER_SE_VERDADEIRO 8; " +
				"CARREGAR 0 1; EXIGIR_BOOL; GUARDAR 0 2; NULO; RETORNAR"},
		{"array e indice", "let a = [1, 2]; a[0] = a[1];",
			"CONST 0; CONST 1; ARRAY 2; GUARDAR 0 0; CARREGAR 0 0; CONST 2; CARREGAR 0 0; CONST 0; INDICE; GUARDAR_INDICE; NULO; RETORNAR"},
		{"bloco com declaracao abre ambiente", "{ let a = 1; print(a); }",
			"ESCOPO 1; CONST 0; GUARDAR 0 0; EMBUTIDO 1; CARREGAR 0 0; CHAMAR 1; POP; FIM_ESCOPO; NULO; RETORNAR"},
		{"bloco sem declaracao nao abre ambiente", "{ print(1); }",
			"EMBUTIDO 0; CONST 1; CHAMAR 1; POP; NULO; RETORNAR"},
		{"sombreamento usa o externo no inicializador", "let x = 1; { let x = x + 1; }",
			"CONST 0; GUARDAR 0 0; ESCOPO 1; CARREGAR 1 0; CONST 0; SOMA; GUARDAR 0 0; FIM_ESCOPO; NULO; RETORNAR"},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			p := compilar(t, c.fonte)
			if got := sequencia(p.Principal); got != c.quer {
				t.Errorf("código =\n%s\nquer\n%s", got, c.quer)
			}
		})
	}
}

func TestFuncoes(t *testing.T) {
	t.Run("parametros e locais", func(t *testing.T) {
		p := compilar(t, "fn f(a, b) { let c = a + b; return c; }")
		f := funcaoPorNome(t, p, "f")
		if f.Aridade != 2 || f.NumVars != 3 {
			t.Errorf("aridade=%d vars=%d, quer 2 e 3", f.Aridade, f.NumVars)
		}
		quer := "CARREGAR 0 0; CARREGAR 0 1; SOMA; GUARDAR 0 2; CARREGAR 0 2; RETORNAR; NULO; RETORNAR"
		if got := sequencia(f); got != quer {
			t.Errorf("código =\n%s\nquer\n%s", got, quer)
		}
		if got := sequencia(p.Principal); got != "FECHO 0; GUARDAR 0 0; NULO; RETORNAR" {
			t.Errorf("principal = %s", got)
		}
	})
	t.Run("closure acessa ambiente externo", func(t *testing.T) {
		p := compilar(t, "fn mk() { let c = 0; return fn() { c = c + 1; return c; }; }")
		interna := funcaoPorNome(t, p, "")
		quer := "CARREGAR 1 0; CONST 1; SOMA; GUARDAR 1 0; CARREGAR 1 0; RETORNAR; NULO; RETORNAR"
		if got := sequencia(interna); got != quer {
			t.Errorf("interna =\n%s\nquer\n%s", got, quer)
		}
		mk := funcaoPorNome(t, p, "mk")
		quer = "CONST 0; GUARDAR 0 0; FECHO 0; RETORNAR; NULO; RETORNAR"
		if got := sequencia(mk); got != quer {
			t.Errorf("mk =\n%s\nquer\n%s", got, quer)
		}
	})
	t.Run("funcoes sao icadas", func(t *testing.T) {
		p := compilar(t, "fn f() { return g(); } fn g() { return 1; }")
		if got := sequencia(p.Principal); got != "FECHO 0; GUARDAR 0 0; FECHO 1; GUARDAR 0 1; NULO; RETORNAR" {
			t.Errorf("principal = %s", got)
		}
		if got := sequencia(funcaoPorNome(t, p, "f")); got != "CARREGAR 1 1; CHAMAR 0; RETORNAR; NULO; RETORNAR" {
			t.Errorf("f = %s", got)
		}
	})
	t.Run("let de funcao anonima recebe nome e permite recursao", func(t *testing.T) {
		p := compilar(t, "let f = fn(n) { return f(n); };")
		f := funcaoPorNome(t, p, "f")
		if got := sequencia(f); got != "CARREGAR 1 0; CARREGAR 0 0; CHAMAR 1; RETORNAR; NULO; RETORNAR" {
			t.Errorf("f = %s", got)
		}
	})
	t.Run("return vazio", func(t *testing.T) {
		p := compilar(t, "fn f() { return; }")
		if got := sequencia(funcaoPorNome(t, p, "f")); got != "NULO; RETORNAR; NULO; RETORNAR" {
			t.Errorf("f = %s", got)
		}
	})
}

func TestErrosDeCompilacao(t *testing.T) {
	casos := []struct {
		nome  string
		fonte string
		quer  string
	}{
		{"variavel indefinida", "print(x);", "1:7: variável 'x' não declarada"},
		{"atribuicao indefinida", "x = 1;", "1:1: variável 'x' não declarada"},
		{"atribuicao a embutido", "len = 1;", "1:1: não é possível atribuir a embutido 'len'"},
		{"return no nivel superior", "return 1;", "1:1: 'return' fora de função"},
		{"uso antes do let", "print(a);\nlet a = 1;", "1:7: variável 'a' não declarada"},
		{"variavel de bloco fora do bloco", "{ let a = 1; }\nprint(a);", "2:7: variável 'a' não declarada"},
		{"primeiro erro prevalece", "print(a); print(b);", "1:7: variável 'a' não declarada"},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			prog, erros := parser.Analisar(c.fonte)
			if len(erros) > 0 {
				t.Fatal(erros)
			}
			p, err := Compilar(prog, embutidos)
			if err == nil || p != nil {
				t.Fatalf("esperado erro, veio %v %v", p, err)
			}
			if err.Error() != c.quer {
				t.Errorf("erro = %q, quer %q", err.Error(), c.quer)
			}
		})
	}
}

func TestEmbutidoSombreado(t *testing.T) {
	p := compilar(t, "let len = 1; print(len);")
	if got := sequencia(p.Principal); got != "CONST 0; GUARDAR 0 0; EMBUTIDO 1; CARREGAR 0 0; CHAMAR 1; POP; NULO; RETORNAR" {
		t.Errorf("código = %s", got)
	}
}

func TestPosicoesPreservadas(t *testing.T) {
	p := compilar(t, "let a = 1;\nlet b = a / 2;")
	var achou bool
	for i, ins := range p.Principal.Codigo {
		if ins.Op == codigo.OpDiv {
			achou = true
			if pos := p.Principal.Posicoes[i]; pos.Linha != 2 || pos.Coluna != 11 {
				t.Errorf("posição da divisão = %v, quer 2:11", pos)
			}
		}
	}
	if !achou {
		t.Error("DIV não encontrado")
	}
}
