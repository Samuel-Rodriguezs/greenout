// Pacote visitor percorre a AST em profundidade (walker) e oferece
// utilitários de consulta construídos sobre o percurso.
package visitor

import (
	"fmt"

	"greenout/comp/ast"
)

// Visitante é chamado para cada nó. Se devolver nil, os filhos do nó são
// ignorados; caso contrário o visitante devolvido percorre os filhos e,
// ao terminar, recebe uma chamada final com nil.
type Visitante interface {
	Visitar(n ast.No) Visitante
}

// Filhos devolve os filhos diretos de n na ordem do código fonte. Os
// identificadores de declaração (let, fn, parâmetros) também são filhos.
func Filhos(n ast.No) []ast.No {
	var fs []ast.No
	add := func(x ast.No) { fs = append(fs, x) }
	switch n := n.(type) {
	case *ast.Programa:
		for _, c := range n.Comandos {
			add(c)
		}
	case *ast.Bloco:
		for _, c := range n.Comandos {
			add(c)
		}
	case *ast.Let:
		add(n.Nome)
		add(n.Valor)
	case *ast.Atribuicao:
		add(n.Alvo)
		add(n.Valor)
	case *ast.Retorno:
		if n.Valor != nil {
			add(n.Valor)
		}
	case *ast.ComandoExpr:
		add(n.Expr)
	case *ast.Se:
		add(n.Cond)
		add(n.Entao)
		if n.Senao != nil {
			add(n.Senao)
		}
	case *ast.Enquanto:
		add(n.Cond)
		add(n.Corpo)
	case *ast.DeclFuncao:
		add(n.Nome)
		for _, p := range n.Params {
			add(p)
		}
		add(n.Corpo)
	case *ast.ArrayLit:
		for _, e := range n.Elementos {
			add(e)
		}
	case *ast.Prefixo:
		add(n.Dir)
	case *ast.Infixo:
		add(n.Esq)
		add(n.Dir)
	case *ast.Acesso:
		add(n.Alvo)
		add(n.Indice)
	case *ast.Chamada:
		add(n.Funcao)
		for _, a := range n.Args {
			add(a)
		}
	case *ast.LiteralFuncao:
		for _, p := range n.Params {
			add(p)
		}
		add(n.Corpo)
	}
	return fs
}

// Percorrer visita n e seus descendentes em pré-ordem.
func Percorrer(v Visitante, n ast.No) {
	if v = v.Visitar(n); v == nil {
		return
	}
	for _, f := range Filhos(n) {
		Percorrer(v, f)
	}
	v.Visitar(nil)
}

type funcVisitante func(ast.No) bool

func (f funcVisitante) Visitar(n ast.No) Visitante {
	if n != nil && f(n) {
		return f
	}
	return nil
}

// Inspecionar chama f para cada nó em pré-ordem; se f devolver false, os
// filhos daquele nó não são visitados.
func Inspecionar(n ast.No, f func(ast.No) bool) {
	Percorrer(funcVisitante(f), n)
}

// Contar devolve quantos nós de cada tipo (ex.: "*ast.Infixo") existem em n.
func Contar(n ast.No) map[string]int {
	res := map[string]int{}
	Inspecionar(n, func(x ast.No) bool {
		res[fmt.Sprintf("%T", x)]++
		return true
	})
	return res
}

// Profundidade devolve a altura da árvore (um nó isolado tem profundidade 1).
func Profundidade(n ast.No) int {
	max := 0
	for _, f := range Filhos(n) {
		if p := Profundidade(f); p > max {
			max = p
		}
	}
	return max + 1
}

// Identificadores devolve, na ordem do fonte, todos os nomes de
// identificadores em n (declarações e usos).
func Identificadores(n ast.No) []string {
	var res []string
	Inspecionar(n, func(x ast.No) bool {
		if id, ok := x.(*ast.Identificador); ok {
			res = append(res, id.Nome)
		}
		return true
	})
	return res
}

// Declarados devolve os nomes introduzidos por let, fn e parâmetros em n.
func Declarados(n ast.No) []string {
	var res []string
	Inspecionar(n, func(x ast.No) bool {
		switch x := x.(type) {
		case *ast.Let:
			res = append(res, x.Nome.Nome)
		case *ast.DeclFuncao:
			res = append(res, x.Nome.Nome)
			res = append(res, ast.NomesParams(x.Params)...)
		case *ast.LiteralFuncao:
			res = append(res, ast.NomesParams(x.Params)...)
		}
		return true
	})
	return res
}
