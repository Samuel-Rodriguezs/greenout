package ast

import (
	"testing"

	"greenout/comp/token"
)

func id(n string) *Identificador { return &Identificador{Nome: n} }
func num(v int64) *Inteiro       { return &Inteiro{Valor: v} }

func TestStringExpressoes(t *testing.T) {
	casos := []struct {
		nome string
		expr Expressao
		quer string
	}{
		{"inteiro", num(42), "42"},
		{"booleano", &Booleano{Valor: true}, "true"},
		{"texto", &Texto{Valor: "a\"b\n"}, `"a\"b\n"`},
		{"ident", id("x"), "x"},
		{"array", &ArrayLit{Elementos: []Expressao{num(1), id("y")}}, "[1, y]"},
		{"array vazio", &ArrayLit{}, "[]"},
		{"prefixo", &Prefixo{Op: "-", Dir: num(3)}, "(-3)"},
		{"infixo aninhado", &Infixo{Op: "+", Esq: num(1), Dir: &Infixo{Op: "*", Esq: num(2), Dir: num(3)}}, "(1 + (2 * 3))"},
		{"acesso", &Acesso{Alvo: id("a"), Indice: num(0)}, "(a[0])"},
		{"chamada", &Chamada{Funcao: id("f"), Args: []Expressao{num(1), num(2)}}, "f(1, 2)"},
		{"funcao", &LiteralFuncao{Params: []*Identificador{id("a"), id("b")}, Corpo: &Bloco{}}, "fn(a, b) {...}"},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := c.expr.String(); got != c.quer {
				t.Errorf("String() = %q, quer %q", got, c.quer)
			}
		})
	}
}

func TestPosicoes(t *testing.T) {
	p := token.Posicao{Linha: 2, Coluna: 3}
	nos := []No{
		&Inteiro{Posicao: p}, &Booleano{Posicao: p}, &Texto{Posicao: p}, &Identificador{Posicao: p},
		&ArrayLit{Posicao: p}, &Prefixo{Posicao: p}, &Infixo{Posicao: p}, &Acesso{Posicao: p},
		&Chamada{Posicao: p}, &LiteralFuncao{Posicao: p}, &Let{Posicao: p}, &Atribuicao{Posicao: p},
		&Retorno{Posicao: p}, &ComandoExpr{Posicao: p}, &Bloco{Posicao: p}, &Se{Posicao: p},
		&Enquanto{Posicao: p}, &DeclFuncao{Posicao: p},
	}
	for _, n := range nos {
		if n.Pos() != p {
			t.Errorf("%T: Pos() = %v, quer %v", n, n.Pos(), p)
		}
	}
}

func TestProgramaPos(t *testing.T) {
	if (&Programa{}).Pos().Valida() {
		t.Error("programa vazio deveria ter posição inválida")
	}
	p := token.Posicao{Linha: 4, Coluna: 1}
	prog := &Programa{Comandos: []Comando{&Retorno{Posicao: p}}}
	if prog.Pos() != p {
		t.Errorf("Pos() = %v, quer %v", prog.Pos(), p)
	}
}

func TestNomesParams(t *testing.T) {
	got := NomesParams([]*Identificador{id("a"), id("b")})
	if len(got) != 2 || got[0] != "a" || got[1] != "b" {
		t.Errorf("NomesParams = %v", got)
	}
	if len(NomesParams(nil)) != 0 {
		t.Error("esperado vazio")
	}
}

// Garante em tempo de compilação que os tipos implementam as interfaces.
var (
	_ Expressao = (*Inteiro)(nil)
	_ Expressao = (*LiteralFuncao)(nil)
	_ Comando   = (*DeclFuncao)(nil)
	_ Comando   = (*Se)(nil)
	_ No        = (*Programa)(nil)
)
