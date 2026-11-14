package visitor

import (
	"reflect"
	"testing"

	"greenout/comp/ast"
	"greenout/comp/parser"
)

func prog(t *testing.T, fonte string) *ast.Programa {
	t.Helper()
	p, erros := parser.Analisar(fonte)
	if len(erros) > 0 {
		t.Fatalf("erros: %v", erros)
	}
	return p
}

const exemplo = `
fn fat(n) {
  if (n <= 1) { return 1; }
  return n * fat(n - 1);
}
let xs = [1, 2, 3];
let f = fn(a, b) { return a + b; };
while (i < 3) { xs[i] = f(xs[i], 1); i = i + 1; }
`

func TestContar(t *testing.T) {
	contagem := Contar(prog(t, "let x = 1 + 2 * 3; print(x);"))
	quer := map[string]int{
		"*ast.Programa": 1, "*ast.Let": 1, "*ast.Identificador": 3, // x, print, x
		"*ast.Infixo": 2, "*ast.Inteiro": 3, "*ast.ComandoExpr": 1, "*ast.Chamada": 1,
	}
	if !reflect.DeepEqual(contagem, quer) {
		t.Errorf("Contar = %v, quer %v", contagem, quer)
	}
}

func TestInspecionarPoda(t *testing.T) {
	p := prog(t, "let f = fn(a) { return a + 1; }; let y = 2 + 3;")
	var infixos int
	Inspecionar(p, func(n ast.No) bool {
		switch n.(type) {
		case *ast.LiteralFuncao:
			return false // não desce na função
		case *ast.Infixo:
			infixos++
		}
		return true
	})
	if infixos != 1 {
		t.Errorf("infixos fora de funções = %d, quer 1", infixos)
	}
}

type registro struct {
	entradas, saidas *int
}

func (r registro) Visitar(n ast.No) Visitante {
	if n == nil {
		*r.saidas++
		return nil
	}
	*r.entradas++
	return r
}

func TestPercorrerChamaNilAoSair(t *testing.T) {
	var e, s int
	Percorrer(registro{&e, &s}, prog(t, "let a = [1, 2];"))
	// Programa, Let, Identificador, ArrayLit, Inteiro, Inteiro = 6 nós
	if e != 6 || s != 6 {
		t.Errorf("entradas=%d saídas=%d, quer 6 e 6", e, s)
	}
}

func TestPercorrerOrdem(t *testing.T) {
	var ordem []string
	Inspecionar(prog(t, "x = f(1) + a[2];"), func(n ast.No) bool {
		switch n := n.(type) {
		case *ast.Identificador:
			ordem = append(ordem, n.Nome)
		case *ast.Inteiro:
			ordem = append(ordem, n.String())
		}
		return true
	})
	quer := []string{"x", "f", "1", "a", "2"}
	if !reflect.DeepEqual(ordem, quer) {
		t.Errorf("ordem = %v, quer %v", ordem, quer)
	}
}

func TestProfundidade(t *testing.T) {
	casos := []struct {
		fonte string
		quer  int
	}{
		{"", 1},
		{"1;", 3},         // Programa > ComandoExpr > Inteiro
		{"1 + 2 * 3;", 5}, // Programa > Cmd > + > * > 3
		{"if (a) { while (b) { c; } }", 7},
	}
	for _, c := range casos {
		if got := Profundidade(prog(t, c.fonte)); got != c.quer {
			t.Errorf("Profundidade(%q) = %d, quer %d", c.fonte, got, c.quer)
		}
	}
}

func TestIdentificadoresEDeclarados(t *testing.T) {
	p := prog(t, exemplo)
	decl := Declarados(p)
	querDecl := []string{"fat", "n", "xs", "f", "a", "b"}
	if !reflect.DeepEqual(decl, querDecl) {
		t.Errorf("Declarados = %v, quer %v", decl, querDecl)
	}
	ids := Identificadores(prog(t, "let a = b + c;"))
	if !reflect.DeepEqual(ids, []string{"a", "b", "c"}) {
		t.Errorf("Identificadores = %v", ids)
	}
}

func TestFilhosNilSeguro(t *testing.T) {
	// return sem valor e if sem else não devem produzir filhos nil
	p := prog(t, "fn f() { return; } if (a) { }")
	for _, f := range Filhos(p.Comandos[0].(*ast.DeclFuncao).Corpo.Comandos[0]) {
		t.Errorf("return vazio não deveria ter filhos: %v", f)
	}
	if n := len(Filhos(p.Comandos[1])); n != 2 {
		t.Errorf("filhos do if sem else = %d, quer 2", n)
	}
	Inspecionar(p, func(n ast.No) bool {
		if n == nil {
			t.Fatal("nó nil visitado")
		}
		return true
	})
}
