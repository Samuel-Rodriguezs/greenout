// Pacote dobra implementa a dobra de constantes (constant folding): expressões
// cujos operandos são literais são substituídas pelo resultado calculado em
// tempo de compilação.
//
// Operações que falhariam em tempo de execução (divisão por zero) e
// combinações de tipos inválidas são deixadas intactas, de modo que a
// dobra nunca altera o comportamento observável do programa.
package dobra

import (
	"greenout/comp/ast"
)

type dobrador struct{ n int }

// Programa dobra as constantes de prog, modificando a árvore no lugar, e
// devolve quantas expressões foram substituídas.
func Programa(prog *ast.Programa) int {
	d := &dobrador{}
	d.comandos(prog.Comandos)
	return d.n
}

// Expressao dobra uma expressão isolada e devolve a expressão resultante.
func Expressao(e ast.Expressao) (ast.Expressao, int) {
	d := &dobrador{}
	r := d.expr(e)
	return r, d.n
}

func (d *dobrador) comandos(cs []ast.Comando) {
	for _, c := range cs {
		d.comando(c)
	}
}

func (d *dobrador) comando(c ast.Comando) {
	switch n := c.(type) {
	case *ast.Let:
		n.Valor = d.expr(n.Valor)
	case *ast.Atribuicao:
		n.Alvo = d.expr(n.Alvo)
		n.Valor = d.expr(n.Valor)
	case *ast.Retorno:
		if n.Valor != nil {
			n.Valor = d.expr(n.Valor)
		}
	case *ast.ComandoExpr:
		n.Expr = d.expr(n.Expr)
	case *ast.Bloco:
		d.comandos(n.Comandos)
	case *ast.Se:
		n.Cond = d.expr(n.Cond)
		d.comando(n.Entao)
		if n.Senao != nil {
			d.comando(n.Senao)
		}
	case *ast.Enquanto:
		n.Cond = d.expr(n.Cond)
		d.comando(n.Corpo)
	case *ast.DeclFuncao:
		d.comando(n.Corpo)
	}
}

func (d *dobrador) expr(e ast.Expressao) ast.Expressao {
	switch n := e.(type) {
	case *ast.ArrayLit:
		for i, el := range n.Elementos {
			n.Elementos[i] = d.expr(el)
		}
	case *ast.Acesso:
		n.Alvo = d.expr(n.Alvo)
		n.Indice = d.expr(n.Indice)
	case *ast.Chamada:
		n.Funcao = d.expr(n.Funcao)
		for i, a := range n.Args {
			n.Args[i] = d.expr(a)
		}
	case *ast.LiteralFuncao:
		d.comando(n.Corpo)
	case *ast.Prefixo:
		n.Dir = d.expr(n.Dir)
		if r := dobrarPrefixo(n); r != nil {
			d.n++
			return r
		}
	case *ast.Infixo:
		n.Esq = d.expr(n.Esq)
		n.Dir = d.expr(n.Dir)
		if r := dobrarInfixo(n); r != nil {
			d.n++
			return r
		}
	}
	return e
}

func dobrarPrefixo(n *ast.Prefixo) ast.Expressao {
	switch v := n.Dir.(type) {
	case *ast.Inteiro:
		if n.Op == "-" {
			return &ast.Inteiro{Posicao: n.Posicao, Valor: -v.Valor}
		}
	case *ast.Booleano:
		if n.Op == "!" {
			return &ast.Booleano{Posicao: n.Posicao, Valor: !v.Valor}
		}
	}
	return nil
}

func dobrarInfixo(n *ast.Infixo) ast.Expressao {
	bool_ := func(b bool) ast.Expressao { return &ast.Booleano{Posicao: n.Posicao, Valor: b} }
	switch l := n.Esq.(type) {
	case *ast.Inteiro:
		r, ok := n.Dir.(*ast.Inteiro)
		if !ok {
			return nil
		}
		a, b := l.Valor, r.Valor
		num := func(v int64) ast.Expressao { return &ast.Inteiro{Posicao: n.Posicao, Valor: v} }
		switch n.Op {
		case "+":
			return num(a + b)
		case "-":
			return num(a - b)
		case "*":
			return num(a * b)
		case "/":
			if b != 0 {
				return num(a / b)
			}
		case "%":
			if b != 0 {
				return num(a % b)
			}
		case "==":
			return bool_(a == b)
		case "!=":
			return bool_(a != b)
		case "<":
			return bool_(a < b)
		case "<=":
			return bool_(a <= b)
		case ">":
			return bool_(a > b)
		case ">=":
			return bool_(a >= b)
		}
	case *ast.Texto:
		r, ok := n.Dir.(*ast.Texto)
		if !ok {
			return nil
		}
		a, b := l.Valor, r.Valor
		switch n.Op {
		case "+":
			return &ast.Texto{Posicao: n.Posicao, Valor: a + b}
		case "==":
			return bool_(a == b)
		case "!=":
			return bool_(a != b)
		case "<":
			return bool_(a < b)
		case "<=":
			return bool_(a <= b)
		case ">":
			return bool_(a > b)
		case ">=":
			return bool_(a >= b)
		}
	case *ast.Booleano:
		// curto-circuito: o lado direito nunca é avaliado, logo pode sumir
		if n.Op == "&&" && !l.Valor {
			return bool_(false)
		}
		if n.Op == "||" && l.Valor {
			return bool_(true)
		}
		if r, ok := n.Dir.(*ast.Booleano); ok {
			switch n.Op {
			case "&&":
				return bool_(l.Valor && r.Valor)
			case "||":
				return bool_(l.Valor || r.Valor)
			case "==":
				return bool_(l.Valor == r.Valor)
			case "!=":
				return bool_(l.Valor != r.Valor)
			}
		}
	}
	return nil
}
