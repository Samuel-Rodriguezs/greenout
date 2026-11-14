// Pacote mortos elimina código morto da AST: ramos de if com condição
// constante, laços que nunca executam, expressões sem efeito colateral
// usadas como comando e comandos após um return.
//
// Deve ser usado depois da dobra de constantes, que transforma condições
// como (1 < 2) em literais. A árvore é modificada no lugar.
package mortos

import (
	"greenout/comp/ast"
	"greenout/comp/visitor"
)

type eliminador struct{ n int }

// Eliminar remove código morto de prog e devolve quantos comandos foram
// removidos ou simplificados.
func Eliminar(prog *ast.Programa) int {
	e := &eliminador{}
	prog.Comandos = e.comandos(prog.Comandos)
	return e.n
}

// pura informa se avaliar a expressão não tem efeito observável nem pode falhar.
func pura(e ast.Expressao) bool {
	switch n := e.(type) {
	case *ast.Inteiro, *ast.Booleano, *ast.Texto, *ast.Identificador, *ast.LiteralFuncao:
		return true
	case *ast.ArrayLit:
		for _, el := range n.Elementos {
			if !pura(el) {
				return false
			}
		}
		return true
	}
	return false
}

// temDeclaracao informa se algum comando direto declara nomes no escopo.
func temDeclaracao(cs []ast.Comando) bool {
	for _, c := range cs {
		switch c.(type) {
		case *ast.Let, *ast.DeclFuncao:
			return true
		}
	}
	return false
}

// expr processa funções anônimas aninhadas em uma expressão.
func (e *eliminador) expr(x ast.Expressao) {
	visitor.Inspecionar(x, func(n ast.No) bool {
		if lf, ok := n.(*ast.LiteralFuncao); ok {
			lf.Corpo.Comandos = e.comandos(lf.Corpo.Comandos)
			return false
		}
		return true
	})
}

// comandos simplifica uma sequência e corta o que vem depois de um return.
func (e *eliminador) comandos(cs []ast.Comando) []ast.Comando {
	var saida []ast.Comando
	for _, c := range cs {
		saida = append(saida, e.comando(c)...)
	}
	for i, c := range saida {
		if _, ok := c.(*ast.Retorno); !ok {
			continue
		}
		cauda := saida[i+1:]
		// Funções declaradas são içadas e podem referenciar nomes da cauda;
		// nesse caso a cauda inteira é preservada.
		if len(cauda) > 0 && !temDeclFuncao(cauda) {
			e.n += len(cauda)
			saida = saida[:i+1]
		}
		break
	}
	return saida
}

func temDeclFuncao(cs []ast.Comando) bool {
	for _, c := range cs {
		if _, ok := c.(*ast.DeclFuncao); ok {
			return true
		}
	}
	return false
}

// comando devolve os comandos que substituem c (nenhum, um ou vários).
func (e *eliminador) comando(c ast.Comando) []ast.Comando {
	switch n := c.(type) {
	case *ast.Let:
		e.expr(n.Valor)
	case *ast.Atribuicao:
		e.expr(n.Alvo)
		e.expr(n.Valor)
	case *ast.Retorno:
		if n.Valor != nil {
			e.expr(n.Valor)
		}
	case *ast.ComandoExpr:
		if pura(n.Expr) {
			e.n++
			return nil
		}
		e.expr(n.Expr)
	case *ast.Bloco:
		n.Comandos = e.comandos(n.Comandos)
		if len(n.Comandos) == 0 {
			e.n++
			return nil
		}
		if !temDeclaracao(n.Comandos) {
			e.n++ // bloco sem declarações não precisa de escopo próprio
			return n.Comandos
		}
	case *ast.Se:
		return e.se(n)
	case *ast.Enquanto:
		if b, ok := n.Cond.(*ast.Booleano); ok && !b.Valor {
			e.n++
			return nil
		}
		e.expr(n.Cond)
		n.Corpo.Comandos = e.comandos(n.Corpo.Comandos)
	case *ast.DeclFuncao:
		n.Corpo.Comandos = e.comandos(n.Corpo.Comandos)
	}
	return []ast.Comando{c}
}

func (e *eliminador) se(n *ast.Se) []ast.Comando {
	if b, ok := n.Cond.(*ast.Booleano); ok {
		e.n++
		if b.Valor {
			return e.comando(n.Entao)
		}
		if n.Senao != nil {
			return e.comando(n.Senao)
		}
		return nil
	}
	e.expr(n.Cond)
	n.Entao.Comandos = e.comandos(n.Entao.Comandos)
	if n.Senao != nil {
		n.Senao = ramo(e.comando(n.Senao))
	}
	return []ast.Comando{n}
}

// ramo converte o resultado da simplificação do else em um Bloco ou Se.
func ramo(cs []ast.Comando) ast.Comando {
	switch {
	case len(cs) == 0:
		return nil
	case len(cs) == 1:
		switch c := cs[0].(type) {
		case *ast.Bloco:
			return c
		case *ast.Se:
			return c
		}
	}
	return &ast.Bloco{Posicao: cs[0].Pos(), Comandos: cs}
}
