// Pacote semantica faz a análise semântica de nomes: resolve identificadores
// com a tabela de símbolos e reporta usos indevidos.
//
// A regra de escopo é léxica e exige declaração antes do uso, com uma
// exceção: funções declaradas com "fn nome" são içadas (hoisting) para o
// início do bloco, permitindo recursão mútua.
package semantica

import (
	"fmt"

	"greenout/comp/ast"
	"greenout/comp/simbolos"
	"greenout/comp/token"
)

// Opcoes configura a análise.
type Opcoes struct {
	Embutidos []string // nomes sempre visíveis (len, print, ...)
}

// Resultado reúne erros (impedem a execução) e avisos (informativos).
type Resultado struct {
	Erros  []*token.Erro
	Avisos []*token.Erro
}

type analisador struct {
	tab *simbolos.Tabela
	res *Resultado
}

// Analisar verifica o programa e devolve erros e avisos em ordem de ocorrência.
func Analisar(prog *ast.Programa, op Opcoes) *Resultado {
	a := &analisador{tab: simbolos.Nova(), res: &Resultado{}}
	for _, n := range op.Embutidos {
		a.tab.DeclararEmbutido(n, nil)
	}
	a.comandos(prog.Comandos)
	return a.res
}

func (a *analisador) erro(pos token.Posicao, formato string, args ...any) {
	a.res.Erros = append(a.res.Erros, token.Errorf(pos, formato, args...))
}

func (a *analisador) declarar(id *ast.Identificador, cat simbolos.Categoria) {
	if ant, err := a.tab.Declarar(id.Nome, cat, id.Posicao); err != nil {
		a.erro(id.Posicao, "%v (declaração anterior em %s)", err, ant.Pos)
	}
}

// comandos analisa uma sequência no escopo corrente, içando funções.
func (a *analisador) comandos(cs []ast.Comando) {
	for _, c := range cs {
		if f, ok := c.(*ast.DeclFuncao); ok {
			a.declarar(f.Nome, simbolos.Funcao)
		}
	}
	for _, c := range cs {
		a.comando(c)
	}
}

func (a *analisador) avisarNaoUsados(e *simbolos.Escopo) {
	if e == nil {
		return
	}
	for _, s := range e.NaoUsados() {
		a.res.Avisos = append(a.res.Avisos, token.Errorf(s.Pos, "variável '%s' declarada e não usada", s.Nome))
	}
}

func (a *analisador) bloco(b *ast.Bloco) {
	a.tab.Entrar(false)
	a.comandos(b.Comandos)
	a.avisarNaoUsados(a.tab.Sair())
}

func (a *analisador) funcao(params []*ast.Identificador, corpo *ast.Bloco) {
	a.tab.Entrar(true)
	for _, p := range params {
		if _, err := a.tab.Declarar(p.Nome, simbolos.Parametro, p.Posicao); err != nil {
			a.erro(p.Posicao, "parâmetro '%s' duplicado", p.Nome)
		}
	}
	a.comandos(corpo.Comandos)
	a.avisarNaoUsados(a.tab.Sair())
}

func (a *analisador) comando(c ast.Comando) {
	switch n := c.(type) {
	case *ast.Let:
		if _, ok := n.Valor.(*ast.LiteralFuncao); ok {
			// permite recursão: o nome já existe dentro da função
			a.declarar(n.Nome, simbolos.Variavel)
			a.expr(n.Valor)
			return
		}
		a.expr(n.Valor)
		a.declarar(n.Nome, simbolos.Variavel)
	case *ast.DeclFuncao:
		a.funcao(n.Params, n.Corpo)
	case *ast.Atribuicao:
		a.atribuicao(n)
	case *ast.Retorno:
		if !a.tab.DentroDeFuncao() {
			a.erro(n.Posicao, "'return' fora de função")
		}
		if n.Valor != nil {
			a.expr(n.Valor)
		}
	case *ast.ComandoExpr:
		a.expr(n.Expr)
	case *ast.Bloco:
		a.bloco(n)
	case *ast.Se:
		a.expr(n.Cond)
		a.bloco(n.Entao)
		if n.Senao != nil {
			a.comando(n.Senao)
		}
	case *ast.Enquanto:
		a.expr(n.Cond)
		a.bloco(n.Corpo)
	}
}

func (a *analisador) atribuicao(n *ast.Atribuicao) {
	a.expr(n.Valor)
	switch alvo := n.Alvo.(type) {
	case *ast.Identificador:
		s, ok := a.tab.Resolver(alvo.Nome)
		switch {
		case !ok:
			a.erro(alvo.Posicao, "atribuição a variável não declarada '%s'", alvo.Nome)
		case s.Categoria == simbolos.Embutido || s.Categoria == simbolos.Funcao:
			a.erro(alvo.Posicao, "não é possível atribuir a %s '%s'", s.Categoria, alvo.Nome)
		}
	default:
		a.expr(alvo)
	}
}

func (a *analisador) expr(e ast.Expressao) {
	switch n := e.(type) {
	case *ast.Identificador:
		if s, ok := a.tab.Resolver(n.Nome); ok {
			s.Usado = true
		} else {
			a.erro(n.Posicao, "variável '%s' não declarada", n.Nome)
		}
	case *ast.ArrayLit:
		for _, el := range n.Elementos {
			a.expr(el)
		}
	case *ast.Prefixo:
		a.expr(n.Dir)
	case *ast.Infixo:
		a.expr(n.Esq)
		a.expr(n.Dir)
	case *ast.Acesso:
		a.expr(n.Alvo)
		a.expr(n.Indice)
	case *ast.Chamada:
		a.expr(n.Funcao)
		for _, arg := range n.Args {
			a.expr(arg)
		}
	case *ast.LiteralFuncao:
		a.funcao(n.Params, n.Corpo)
	}
}

// Mensagens devolve os erros como texto "linha:coluna: mensagem".
func (r *Resultado) Mensagens() []string {
	var ms []string
	for _, e := range r.Erros {
		ms = append(ms, e.Error())
	}
	return ms
}

func (r *Resultado) String() string {
	return fmt.Sprintf("%d erro(s), %d aviso(s)", len(r.Erros), len(r.Avisos))
}
