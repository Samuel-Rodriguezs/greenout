// Pacote ast define a árvore sintática abstrata da linguagem Mini.
//
// Há duas famílias de nós: Expressao (produzem valor) e Comando (executam
// efeitos). Todos os nós são ponteiros e carregam sua Posicao no fonte.
package ast

import (
	"fmt"
	"strconv"
	"strings"

	"greenout/comp/token"
)

// No é qualquer nó da árvore.
type No interface {
	Pos() token.Posicao
}

// Expressao é um nó que produz valor. String devolve uma forma textual
// totalmente parentesizada, útil para depurar a precedência.
type Expressao interface {
	No
	String() string
	exprNo()
}

// Comando é um nó que não produz valor.
type Comando interface {
	No
	cmdNo()
}

// ---- Expressões ----

type Inteiro struct {
	Posicao token.Posicao
	Valor   int64
}

type Booleano struct {
	Posicao token.Posicao
	Valor   bool
}

type Texto struct {
	Posicao token.Posicao
	Valor   string
}

type Identificador struct {
	Posicao token.Posicao
	Nome    string
}

// ArrayLit é o literal [a, b, c].
type ArrayLit struct {
	Posicao   token.Posicao
	Elementos []Expressao
}

// Prefixo é um operador unário: - ou !.
type Prefixo struct {
	Posicao token.Posicao
	Op      string
	Dir     Expressao
}

// Infixo é um operador binário.
type Infixo struct {
	Posicao token.Posicao
	Op      string
	Esq     Expressao
	Dir     Expressao
}

// Acesso é a indexação alvo[indice].
type Acesso struct {
	Posicao token.Posicao
	Alvo    Expressao
	Indice  Expressao
}

// Chamada é a aplicação funcao(args...).
type Chamada struct {
	Posicao token.Posicao
	Funcao  Expressao
	Args    []Expressao
}

// LiteralFuncao é a função anônima fn(a, b) { ... }.
type LiteralFuncao struct {
	Posicao token.Posicao
	Params  []*Identificador
	Corpo   *Bloco
}

// ---- Comandos ----

// Let declara uma variável no escopo atual.
type Let struct {
	Posicao token.Posicao
	Nome    *Identificador
	Valor   Expressao
}

// Atribuicao altera uma variável ou posição de array. Alvo é um
// *Identificador ou um *Acesso.
type Atribuicao struct {
	Posicao token.Posicao
	Alvo    Expressao
	Valor   Expressao
}

// Retorno encerra a função; Valor pode ser nil.
type Retorno struct {
	Posicao token.Posicao
	Valor   Expressao
}

// ComandoExpr é uma expressão usada como comando.
type ComandoExpr struct {
	Posicao token.Posicao
	Expr    Expressao
}

type Bloco struct {
	Posicao  token.Posicao
	Comandos []Comando
}

// Se é o condicional. Senao é nil, um *Bloco ou outro *Se (else if).
type Se struct {
	Posicao token.Posicao
	Cond    Expressao
	Entao   *Bloco
	Senao   Comando
}

type Enquanto struct {
	Posicao token.Posicao
	Cond    Expressao
	Corpo   *Bloco
}

// DeclFuncao é a declaração fn nome(params) { ... }.
type DeclFuncao struct {
	Posicao token.Posicao
	Nome    *Identificador
	Params  []*Identificador
	Corpo   *Bloco
}

// Programa é a raiz da árvore.
type Programa struct {
	Comandos []Comando
}

func (n *Inteiro) Pos() token.Posicao       { return n.Posicao }
func (n *Booleano) Pos() token.Posicao      { return n.Posicao }
func (n *Texto) Pos() token.Posicao         { return n.Posicao }
func (n *Identificador) Pos() token.Posicao { return n.Posicao }
func (n *ArrayLit) Pos() token.Posicao      { return n.Posicao }
func (n *Prefixo) Pos() token.Posicao       { return n.Posicao }
func (n *Infixo) Pos() token.Posicao        { return n.Posicao }
func (n *Acesso) Pos() token.Posicao        { return n.Posicao }
func (n *Chamada) Pos() token.Posicao       { return n.Posicao }
func (n *LiteralFuncao) Pos() token.Posicao { return n.Posicao }
func (n *Let) Pos() token.Posicao           { return n.Posicao }
func (n *Atribuicao) Pos() token.Posicao    { return n.Posicao }
func (n *Retorno) Pos() token.Posicao       { return n.Posicao }
func (n *ComandoExpr) Pos() token.Posicao   { return n.Posicao }
func (n *Bloco) Pos() token.Posicao         { return n.Posicao }
func (n *Se) Pos() token.Posicao            { return n.Posicao }
func (n *Enquanto) Pos() token.Posicao      { return n.Posicao }
func (n *DeclFuncao) Pos() token.Posicao    { return n.Posicao }

// Pos do programa é o início do primeiro comando, ou a posição zero.
func (n *Programa) Pos() token.Posicao {
	if len(n.Comandos) > 0 {
		return n.Comandos[0].Pos()
	}
	return token.Posicao{}
}

func (*Inteiro) exprNo()       {}
func (*Booleano) exprNo()      {}
func (*Texto) exprNo()         {}
func (*Identificador) exprNo() {}
func (*ArrayLit) exprNo()      {}
func (*Prefixo) exprNo()       {}
func (*Infixo) exprNo()        {}
func (*Acesso) exprNo()        {}
func (*Chamada) exprNo()       {}
func (*LiteralFuncao) exprNo() {}

func (*Let) cmdNo()         {}
func (*Atribuicao) cmdNo()  {}
func (*Retorno) cmdNo()     {}
func (*ComandoExpr) cmdNo() {}
func (*Bloco) cmdNo()       {}
func (*Se) cmdNo()          {}
func (*Enquanto) cmdNo()    {}
func (*DeclFuncao) cmdNo()  {}

func (n *Inteiro) String() string       { return strconv.FormatInt(n.Valor, 10) }
func (n *Booleano) String() string      { return strconv.FormatBool(n.Valor) }
func (n *Texto) String() string         { return strconv.Quote(n.Valor) }
func (n *Identificador) String() string { return n.Nome }
func (n *ArrayLit) String() string      { return "[" + juntar(n.Elementos) + "]" }
func (n *Prefixo) String() string       { return "(" + n.Op + n.Dir.String() + ")" }
func (n *Infixo) String() string {
	return "(" + n.Esq.String() + " " + n.Op + " " + n.Dir.String() + ")"
}
func (n *Acesso) String() string  { return "(" + n.Alvo.String() + "[" + n.Indice.String() + "])" }
func (n *Chamada) String() string { return n.Funcao.String() + "(" + juntar(n.Args) + ")" }
func (n *LiteralFuncao) String() string {
	return fmt.Sprintf("fn(%s) {...}", nomes(n.Params))
}

func juntar(es []Expressao) string {
	partes := make([]string, len(es))
	for i, e := range es {
		partes[i] = e.String()
	}
	return strings.Join(partes, ", ")
}

func nomes(ids []*Identificador) string {
	partes := make([]string, len(ids))
	for i, id := range ids {
		partes[i] = id.Nome
	}
	return strings.Join(partes, ", ")
}

// NomesParams devolve os nomes dos parâmetros.
func NomesParams(ids []*Identificador) []string {
	res := make([]string, len(ids))
	for i, id := range ids {
		res[i] = id.Nome
	}
	return res
}
