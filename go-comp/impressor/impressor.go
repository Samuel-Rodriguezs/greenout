// Pacote impressor converte uma AST de volta em código Mini formatado
// (pretty printer), com indentação de dois espaços e parênteses mínimos.
package impressor

import (
	"strings"

	"greenout/comp/ast"
	"greenout/comp/parser"
)

type impressor struct {
	sb    strings.Builder
	nivel int
}

// Formatar devolve o programa formatado, com uma quebra de linha final.
func Formatar(prog *ast.Programa) string {
	im := &impressor{}
	for _, c := range prog.Comandos {
		im.comando(c)
	}
	return im.sb.String()
}

// FormatarExpr devolve uma única expressão formatada.
func FormatarExpr(e ast.Expressao) string {
	im := &impressor{}
	im.expr(e, 0)
	return im.sb.String()
}

func (im *impressor) escrever(s string) { im.sb.WriteString(s) }

func (im *impressor) indentar() {
	im.sb.WriteString(strings.Repeat("  ", im.nivel))
}

// comando escreve o comando em linhas próprias, já indentado.
func (im *impressor) comando(c ast.Comando) {
	im.indentar()
	im.comandoSemIndent(c)
	im.escrever("\n")
}

func (im *impressor) comandoSemIndent(c ast.Comando) {
	switch n := c.(type) {
	case *ast.Let:
		im.escrever("let " + n.Nome.Nome + " = ")
		im.expr(n.Valor, 0)
		im.escrever(";")
	case *ast.Atribuicao:
		im.expr(n.Alvo, 0)
		im.escrever(" = ")
		im.expr(n.Valor, 0)
		im.escrever(";")
	case *ast.Retorno:
		im.escrever("return")
		if n.Valor != nil {
			im.escrever(" ")
			im.expr(n.Valor, 0)
		}
		im.escrever(";")
	case *ast.ComandoExpr:
		im.expr(n.Expr, 0)
		im.escrever(";")
	case *ast.Bloco:
		im.bloco(n)
	case *ast.Se:
		im.se(n)
	case *ast.Enquanto:
		im.escrever("while (")
		im.expr(n.Cond, 0)
		im.escrever(") ")
		im.bloco(n.Corpo)
	case *ast.DeclFuncao:
		im.escrever("fn " + n.Nome.Nome)
		im.params(n.Params)
		im.escrever(" ")
		im.bloco(n.Corpo)
	}
}

func (im *impressor) se(n *ast.Se) {
	im.escrever("if (")
	im.expr(n.Cond, 0)
	im.escrever(") ")
	im.bloco(n.Entao)
	switch s := n.Senao.(type) {
	case *ast.Bloco:
		im.escrever(" else ")
		im.bloco(s)
	case *ast.Se:
		im.escrever(" else ")
		im.se(s)
	}
}

func (im *impressor) params(ps []*ast.Identificador) {
	im.escrever("(")
	for i, p := range ps {
		if i > 0 {
			im.escrever(", ")
		}
		im.escrever(p.Nome)
	}
	im.escrever(")")
}

// bloco escreve "{ ... }" sem indentar a primeira linha nem quebrar a última.
func (im *impressor) bloco(b *ast.Bloco) {
	if len(b.Comandos) == 0 {
		im.escrever("{}")
		return
	}
	im.escrever("{\n")
	im.nivel++
	for _, c := range b.Comandos {
		im.comando(c)
	}
	im.nivel--
	im.indentar()
	im.escrever("}")
}

// expr escreve e, colocando parênteses se sua precedência for menor que min.
func (im *impressor) expr(e ast.Expressao, min int) {
	switch n := e.(type) {
	case *ast.Inteiro, *ast.Booleano, *ast.Identificador:
		im.escrever(n.String())
	case *ast.Texto:
		im.escrever(texto(n.Valor))
	case *ast.ArrayLit:
		im.escrever("[")
		im.lista(n.Elementos)
		im.escrever("]")
	case *ast.Prefixo:
		im.escrever(n.Op)
		im.expr(n.Dir, parser.PrecPrefixo)
	case *ast.Infixo:
		p := parser.PrecedenciaOp(n.Op)
		if p < min {
			im.escrever("(")
		}
		im.expr(n.Esq, p)
		im.escrever(" " + n.Op + " ")
		im.expr(n.Dir, p+1)
		if p < min {
			im.escrever(")")
		}
	case *ast.Acesso:
		im.alvoPosfixo(n.Alvo)
		im.escrever("[")
		im.expr(n.Indice, 0)
		im.escrever("]")
	case *ast.Chamada:
		im.alvoPosfixo(n.Funcao)
		im.escrever("(")
		im.lista(n.Args)
		im.escrever(")")
	case *ast.LiteralFuncao:
		im.escrever("fn")
		im.params(n.Params)
		im.escrever(" ")
		im.bloco(n.Corpo)
	}
}

// alvoPosfixo parentesiza alvos de chamada/indexação que não sejam primários.
func (im *impressor) alvoPosfixo(e ast.Expressao) {
	switch e.(type) {
	case *ast.Infixo, *ast.Prefixo:
		im.escrever("(")
		im.expr(e, 0)
		im.escrever(")")
	default:
		im.expr(e, 0)
	}
}

func (im *impressor) lista(es []ast.Expressao) {
	for i, e := range es {
		if i > 0 {
			im.escrever(", ")
		}
		im.expr(e, 0)
	}
}

// texto reescreve o literal com os mesmos escapes que o lexer entende.
func texto(s string) string {
	var sb strings.Builder
	sb.WriteByte('"')
	for i := 0; i < len(s); i++ {
		switch c := s[i]; c {
		case '"':
			sb.WriteString(`\"`)
		case '\\':
			sb.WriteString(`\\`)
		case '\n':
			sb.WriteString(`\n`)
		case '\t':
			sb.WriteString(`\t`)
		case '\r':
			sb.WriteString(`\r`)
		default:
			sb.WriteByte(c)
		}
	}
	sb.WriteByte('"')
	return sb.String()
}
