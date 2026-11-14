// Pacote compilador traduz a AST de Mini para bytecode da máquina de pilha.
//
// Os escopos do compilador espelham os ambientes de execução: cada função e
// cada bloco com declarações vira um ambiente, e uma variável é endereçada
// por (saltos de ambiente, posição). Assim a VM reproduz exatamente as
// closures do interpretador, inclusive uma variável nova por iteração de laço.
package compilador

import (
	"greenout/comp/ast"
	"greenout/comp/codigo"
	"greenout/comp/interp"
	"greenout/comp/token"
)

// escopo corresponde a um ambiente em tempo de execução.
type escopo struct {
	pai   *escopo
	nomes map[string]int
	n     int
}

type compilador struct {
	prog      *codigo.Programa
	atual     *codigo.Funcao
	esc       *escopo
	emb       map[string]bool
	inteiros  map[int64]int
	textos    map[string]int
	emFuncao  bool
	pendentes map[*ast.DeclFuncao]*codigo.Funcao
	err       *token.Erro
}

// Compilar gera o programa de bytecode. embutidos lista os nomes das funções
// nativas que a VM fornecerá. Devolve o primeiro erro encontrado, se houver.
func Compilar(prog *ast.Programa, embutidos []string) (*codigo.Programa, error) {
	c := &compilador{
		prog:      &codigo.Programa{},
		emb:       map[string]bool{},
		inteiros:  map[int64]int{},
		textos:    map[string]int{},
		pendentes: map[*ast.DeclFuncao]*codigo.Funcao{},
	}
	for _, e := range embutidos {
		c.emb[e] = true
	}
	main := &codigo.Funcao{Nome: "principal", NumVars: contarDecl(prog.Comandos)}
	c.prog.Principal = main
	c.atual = main
	c.esc = &escopo{nomes: map[string]int{}}
	c.sequencia(prog.Comandos)
	c.emitir(codigo.OpNulo, 0, 0, token.Posicao{})
	c.emitir(codigo.OpRetornar, 0, 0, token.Posicao{})
	if c.err != nil {
		return nil, c.err
	}
	return c.prog, nil
}

func (c *compilador) erro(pos token.Posicao, formato string, args ...any) {
	if c.err == nil {
		c.err = token.Errorf(pos, formato, args...)
	}
}

func (c *compilador) emitir(op codigo.Opcode, a, b int, pos token.Posicao) int {
	return c.atual.Emitir(op, a, b, pos)
}

func (c *compilador) aqui() int { return len(c.atual.Codigo) }

// contarDecl conta as declarações (let e fn) diretas de uma sequência.
func contarDecl(cs []ast.Comando) int {
	n := 0
	for _, cmd := range cs {
		switch cmd.(type) {
		case *ast.Let, *ast.DeclFuncao:
			n++
		}
	}
	return n
}

func (c *compilador) constante(v interp.Valor) int {
	switch x := v.(type) {
	case interp.Inteiro:
		if i, ok := c.inteiros[int64(x)]; ok {
			return i
		}
		c.prog.Constantes = append(c.prog.Constantes, v)
		c.inteiros[int64(x)] = len(c.prog.Constantes) - 1
		return len(c.prog.Constantes) - 1
	case interp.Texto:
		if i, ok := c.textos[string(x)]; ok {
			return i
		}
		c.prog.Constantes = append(c.prog.Constantes, v)
		c.textos[string(x)] = len(c.prog.Constantes) - 1
		return len(c.prog.Constantes) - 1
	}
	c.prog.Constantes = append(c.prog.Constantes, v)
	return len(c.prog.Constantes) - 1
}

func (c *compilador) declarar(nome string) int {
	slot := c.esc.n
	c.esc.nomes[nome] = slot
	c.esc.n++
	return slot
}

// resolver procura a variável nos ambientes, do mais interno para fora.
func (c *compilador) resolver(nome string) (saltos, slot int, ok bool) {
	for e := c.esc; e != nil; e = e.pai {
		if s, existe := e.nomes[nome]; existe {
			return saltos, s, true
		}
		saltos++
	}
	return 0, 0, false
}

// sequencia compila comandos no escopo corrente. As funções "fn nome" são
// içadas: seus nomes e fechos existem desde o início da sequência (permitindo
// chamadas antes da declaração e recursão mútua), mas o corpo só é compilado
// na posição textual da declaração, quando as variáveis anteriores já estão
// visíveis.
func (c *compilador) sequencia(cs []ast.Comando) {
	for _, cmd := range cs {
		if f, ok := cmd.(*ast.DeclFuncao); ok {
			c.declarar(f.Nome.Nome)
		}
	}
	for _, cmd := range cs {
		if f, ok := cmd.(*ast.DeclFuncao); ok {
			fn, idx := c.reservar(f.Nome.Nome, f.Params, f.Corpo)
			c.pendentes[f] = fn
			c.emitir(codigo.OpFecho, idx, 0, f.Posicao)
			c.emitir(codigo.OpGuardar, 0, c.esc.nomes[f.Nome.Nome], f.Posicao)
		}
	}
	for _, cmd := range cs {
		c.comando(cmd)
	}
}

// reservar cria a função na tabela, ainda sem código, e devolve seu índice.
func (c *compilador) reservar(nome string, params []*ast.Identificador, corpo *ast.Bloco) (*codigo.Funcao, int) {
	f := &codigo.Funcao{Nome: nome, Aridade: len(params), NumVars: len(params) + contarDecl(corpo.Comandos)}
	c.prog.Funcoes = append(c.prog.Funcoes, f)
	return f, len(c.prog.Funcoes) - 1
}

// corpo compila o código de uma função reservada em um novo ambiente.
func (c *compilador) corpo(f *codigo.Funcao, params []*ast.Identificador, corpo *ast.Bloco) {
	salvaFunc, salvaEsc, salvaEm := c.atual, c.esc, c.emFuncao
	c.atual, c.emFuncao = f, true
	c.esc = &escopo{pai: salvaEsc, nomes: map[string]int{}}
	for _, p := range params {
		c.declarar(p.Nome)
	}
	c.sequencia(corpo.Comandos)
	c.emitir(codigo.OpNulo, 0, 0, corpo.Posicao)
	c.emitir(codigo.OpRetornar, 0, 0, corpo.Posicao)
	c.atual, c.esc, c.emFuncao = salvaFunc, salvaEsc, salvaEm
}

// funcao reserva e compila de imediato (funções anônimas e let de função).
func (c *compilador) funcao(nome string, params []*ast.Identificador, corpo *ast.Bloco) int {
	f, idx := c.reservar(nome, params, corpo)
	c.corpo(f, params, corpo)
	return idx
}

func (c *compilador) bloco(b *ast.Bloco) {
	n := contarDecl(b.Comandos)
	if n == 0 {
		c.sequencia(b.Comandos)
		return
	}
	c.emitir(codigo.OpEscopo, n, 0, b.Posicao)
	c.esc = &escopo{pai: c.esc, nomes: map[string]int{}}
	c.sequencia(b.Comandos)
	c.esc = c.esc.pai
	c.emitir(codigo.OpFimEscopo, 0, 0, b.Posicao)
}

func (c *compilador) comando(cmd ast.Comando) {
	switch n := cmd.(type) {
	case *ast.Let:
		if lit, ok := n.Valor.(*ast.LiteralFuncao); ok {
			slot := c.declarar(n.Nome.Nome) // permite recursão pelo próprio nome
			idx := c.funcao(n.Nome.Nome, lit.Params, lit.Corpo)
			c.emitir(codigo.OpFecho, idx, 0, lit.Posicao)
			c.emitir(codigo.OpGuardar, 0, slot, n.Posicao)
			return
		}
		c.expr(n.Valor)
		slot := c.declarar(n.Nome.Nome)
		c.emitir(codigo.OpGuardar, 0, slot, n.Posicao)
	case *ast.Atribuicao:
		c.atribuicao(n)
	case *ast.Retorno:
		if !c.emFuncao {
			c.erro(n.Posicao, "'return' fora de função")
			return
		}
		if n.Valor == nil {
			c.emitir(codigo.OpNulo, 0, 0, n.Posicao)
		} else {
			c.expr(n.Valor)
		}
		c.emitir(codigo.OpRetornar, 0, 0, n.Posicao)
	case *ast.ComandoExpr:
		c.expr(n.Expr)
		c.emitir(codigo.OpPop, 0, 0, n.Posicao)
	case *ast.Bloco:
		c.bloco(n)
	case *ast.Se:
		c.expr(n.Cond)
		jf := c.emitir(codigo.OpSaltoSeFalso, 0, 0, n.Cond.Pos())
		c.bloco(n.Entao)
		if n.Senao == nil {
			c.atual.Remendar(jf, c.aqui())
			return
		}
		fim := c.emitir(codigo.OpSalto, 0, 0, n.Posicao)
		c.atual.Remendar(jf, c.aqui())
		c.comando(n.Senao)
		c.atual.Remendar(fim, c.aqui())
	case *ast.Enquanto:
		inicio := c.aqui()
		c.expr(n.Cond)
		jf := c.emitir(codigo.OpSaltoSeFalso, 0, 0, n.Cond.Pos())
		c.bloco(n.Corpo)
		c.emitir(codigo.OpSalto, inicio, 0, n.Posicao)
		c.atual.Remendar(jf, c.aqui())
	case *ast.DeclFuncao:
		c.corpo(c.pendentes[n], n.Params, n.Corpo)
	}
}

func (c *compilador) atribuicao(n *ast.Atribuicao) {
	switch alvo := n.Alvo.(type) {
	case *ast.Identificador:
		c.expr(n.Valor)
		saltos, slot, ok := c.resolver(alvo.Nome)
		if !ok {
			if c.emb[alvo.Nome] {
				c.erro(alvo.Posicao, "não é possível atribuir a embutido '%s'", alvo.Nome)
			} else {
				c.erro(alvo.Posicao, "variável '%s' não declarada", alvo.Nome)
			}
			return
		}
		c.emitir(codigo.OpGuardar, saltos, slot, n.Posicao)
	case *ast.Acesso:
		c.expr(alvo.Alvo)
		c.expr(alvo.Indice)
		c.expr(n.Valor)
		c.emitir(codigo.OpGuardarIndice, 0, 0, alvo.Posicao)
	default:
		c.erro(n.Posicao, "alvo de atribuição inválido")
	}
}

func (c *compilador) expr(e ast.Expressao) {
	switch n := e.(type) {
	case *ast.Inteiro:
		c.emitir(codigo.OpConst, c.constante(interp.Inteiro(n.Valor)), 0, n.Posicao)
	case *ast.Texto:
		c.emitir(codigo.OpConst, c.constante(interp.Texto(n.Valor)), 0, n.Posicao)
	case *ast.Booleano:
		op := codigo.OpFalso
		if n.Valor {
			op = codigo.OpVerdadeiro
		}
		c.emitir(op, 0, 0, n.Posicao)
	case *ast.Identificador:
		if saltos, slot, ok := c.resolver(n.Nome); ok {
			c.emitir(codigo.OpCarregar, saltos, slot, n.Posicao)
		} else if c.emb[n.Nome] {
			c.emitir(codigo.OpEmbutido, c.constante(interp.Texto(n.Nome)), 0, n.Posicao)
		} else {
			c.erro(n.Posicao, "variável '%s' não declarada", n.Nome)
		}
	case *ast.ArrayLit:
		for _, el := range n.Elementos {
			c.expr(el)
		}
		c.emitir(codigo.OpArray, len(n.Elementos), 0, n.Posicao)
	case *ast.Prefixo:
		c.expr(n.Dir)
		op := codigo.OpNeg
		if n.Op == "!" {
			op = codigo.OpNao
		}
		c.emitir(op, 0, 0, n.Posicao)
	case *ast.Infixo:
		c.infixo(n)
	case *ast.Acesso:
		c.expr(n.Alvo)
		c.expr(n.Indice)
		c.emitir(codigo.OpIndice, 0, 0, n.Posicao)
	case *ast.Chamada:
		c.expr(n.Funcao)
		for _, a := range n.Args {
			c.expr(a)
		}
		c.emitir(codigo.OpChamar, len(n.Args), 0, n.Posicao)
	case *ast.LiteralFuncao:
		idx := c.funcao("", n.Params, n.Corpo)
		c.emitir(codigo.OpFecho, idx, 0, n.Posicao)
	}
}

func (c *compilador) infixo(n *ast.Infixo) {
	if n.Op == "&&" || n.Op == "||" {
		salto := codigo.OpManterSeFalso
		if n.Op == "||" {
			salto = codigo.OpManterSeVerdadeiro
		}
		c.expr(n.Esq)
		j := c.emitir(salto, 0, 0, n.Posicao)
		c.expr(n.Dir)
		c.emitir(codigo.OpExigirBool, 0, 0, n.Posicao)
		c.atual.Remendar(j, c.aqui())
		return
	}
	op, ok := codigo.DeOperador(n.Op)
	if !ok {
		c.erro(n.Posicao, "operador desconhecido '%s'", n.Op)
		return
	}
	c.expr(n.Esq)
	c.expr(n.Dir)
	c.emitir(op, 0, 0, n.Posicao)
}
