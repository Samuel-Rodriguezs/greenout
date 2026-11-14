// Pacote parser implementa o analisador sintático da linguagem Mini com
// expressões por precedência (Pratt) e recuperação de erros.
package parser

import (
	"strconv"

	"greenout/comp/ast"
	"greenout/comp/lexer"
	"greenout/comp/token"
)

// Níveis de precedência, do mais fraco ao mais forte.
const (
	pMin = iota
	pOu
	pE
	pIgualdade
	pComparacao
	pSoma
	pProduto
	pPrefixo
	pChamada
)

// PrecPrefixo é a precedência dos operadores unários (- e !).
const PrecPrefixo = pPrefixo

var precedenciaTok = map[token.Tipo]int{
	token.Ou: pOu, token.E: pE,
	token.Igual: pIgualdade, token.Diferente: pIgualdade,
	token.Menor: pComparacao, token.MenorIgual: pComparacao,
	token.Maior: pComparacao, token.MaiorIgual: pComparacao,
	token.Mais: pSoma, token.Menos: pSoma,
	token.Asterisco: pProduto, token.Barra: pProduto, token.Resto: pProduto,
	token.ParenAbre: pChamada, token.ColcheteAbre: pChamada,
}

var precedenciaOp = map[string]int{
	"||": pOu, "&&": pE, "==": pIgualdade, "!=": pIgualdade,
	"<": pComparacao, "<=": pComparacao, ">": pComparacao, ">=": pComparacao,
	"+": pSoma, "-": pSoma, "*": pProduto, "/": pProduto, "%": pProduto,
}

// PrecedenciaOp devolve a precedência de um operador binário (0 se desconhecido).
func PrecedenciaOp(op string) int { return precedenciaOp[op] }

const profundidadeMax = 500

// Parser consome os tokens e constrói a AST acumulando erros.
type Parser struct {
	toks  []token.Token
	i     int
	erros []*token.Erro
	prof  int
}

// Novo cria um parser para o fonte.
func Novo(fonte string) *Parser {
	return &Parser{toks: lexer.Tokens(fonte)}
}

// Analisar é um atalho que analisa o fonte inteiro.
func Analisar(fonte string) (*ast.Programa, []*token.Erro) {
	p := Novo(fonte)
	prog := p.Programa()
	return prog, p.Erros()
}

// Erros devolve os erros acumulados.
func (p *Parser) Erros() []*token.Erro { return p.erros }

func (p *Parser) atual() token.Token { return p.toks[p.i] }

func (p *Parser) seguinte() token.Token {
	if p.i+1 < len(p.toks) {
		return p.toks[p.i+1]
	}
	return p.toks[len(p.toks)-1]
}

func (p *Parser) avancar() token.Token {
	t := p.toks[p.i]
	if p.i < len(p.toks)-1 {
		p.i++
	}
	return t
}

// descrever produz uma descrição legível do token para mensagens.
func descrever(t token.Token) string {
	switch t.Tipo {
	case token.FimArquivo:
		return "fim do arquivo"
	case token.Ident:
		return "identificador '" + t.Literal + "'"
	case token.Inteiro:
		return "número " + t.Literal
	case token.Texto:
		return "texto " + strconv.Quote(t.Literal)
	}
	return "'" + t.Tipo.String() + "'"
}

// erro registra um erro, ignorando repetições na mesma posição.
func (p *Parser) erro(pos token.Posicao, formato string, args ...any) {
	if n := len(p.erros); n > 0 && p.erros[n-1].Posicao.Deslocamento == pos.Deslocamento {
		return
	}
	p.erros = append(p.erros, token.Errorf(pos, formato, args...))
}

// esperar consome um token do tipo t ou registra erro.
func (p *Parser) esperar(t token.Tipo) (token.Token, bool) {
	tk := p.atual()
	if tk.Tipo == t {
		return p.avancar(), true
	}
	if tk.Tipo == token.Ilegal {
		p.erro(tk.Pos, "%s", tk.Literal)
	} else {
		p.erro(tk.Pos, "esperado '%s', encontrado %s", t, descrever(tk))
	}
	return tk, false
}

// sincronizar descarta tokens até um ponto seguro para retomar a análise:
// depois de um ';' ou antes de um '}' ou palavra-chave de comando, ignorando
// o que estiver dentro de chaves abertas durante o descarte.
func (p *Parser) sincronizar() {
	prof := 0
	for p.atual().Tipo != token.FimArquivo {
		switch p.atual().Tipo {
		case token.PontoVirgula:
			if prof == 0 {
				p.avancar()
				return
			}
		case token.ChaveAbre:
			prof++
		case token.ChaveFecha:
			if prof == 0 {
				return
			}
			prof--
		case token.Let, token.Fn, token.Se, token.Enquanto, token.Retorna:
			if prof == 0 {
				return
			}
		}
		p.avancar()
	}
}

// Programa analisa todos os comandos até o fim do arquivo.
func (p *Parser) Programa() *ast.Programa {
	prog := &ast.Programa{}
	for p.atual().Tipo != token.FimArquivo {
		ini := p.i
		if c := p.comando(); c != nil {
			prog.Comandos = append(prog.Comandos, c)
			continue
		}
		p.sincronizar()
		if p.i == ini {
			p.avancar()
		}
	}
	return prog
}

func (p *Parser) comando() ast.Comando {
	switch p.atual().Tipo {
	case token.Let:
		if c := p.let(); c != nil {
			return c
		}
	case token.Retorna:
		if c := p.retorno(); c != nil {
			return c
		}
	case token.Se:
		if c := p.se(); c != nil {
			return c
		}
	case token.Enquanto:
		if c := p.enquanto(); c != nil {
			return c
		}
	case token.ChaveAbre:
		if c := p.bloco(); c != nil {
			return c
		}
	case token.Fn:
		if p.seguinte().Tipo == token.Ident {
			if c := p.declFuncao(); c != nil {
				return c
			}
			return nil
		}
		return p.exprCmd()
	default:
		return p.exprCmd()
	}
	return nil
}

func (p *Parser) let() *ast.Let {
	pos := p.avancar().Pos
	nome, ok := p.esperar(token.Ident)
	if !ok {
		return nil
	}
	if _, ok := p.esperar(token.Atribui); !ok {
		return nil
	}
	v := p.expr(pMin)
	if v == nil {
		return nil
	}
	if _, ok := p.esperar(token.PontoVirgula); !ok {
		return nil
	}
	return &ast.Let{Posicao: pos, Nome: &ast.Identificador{Posicao: nome.Pos, Nome: nome.Literal}, Valor: v}
}

func (p *Parser) retorno() *ast.Retorno {
	pos := p.avancar().Pos
	var v ast.Expressao
	if p.atual().Tipo != token.PontoVirgula {
		if v = p.expr(pMin); v == nil {
			return nil
		}
	}
	if _, ok := p.esperar(token.PontoVirgula); !ok {
		return nil
	}
	return &ast.Retorno{Posicao: pos, Valor: v}
}

func (p *Parser) se() *ast.Se {
	pos := p.avancar().Pos
	if _, ok := p.esperar(token.ParenAbre); !ok {
		return nil
	}
	cond := p.expr(pMin)
	if cond == nil {
		return nil
	}
	if _, ok := p.esperar(token.ParenFecha); !ok {
		return nil
	}
	entao := p.bloco()
	if entao == nil {
		return nil
	}
	n := &ast.Se{Posicao: pos, Cond: cond, Entao: entao}
	if p.atual().Tipo == token.Senao {
		p.avancar()
		if p.atual().Tipo == token.Se {
			s := p.se()
			if s == nil {
				return nil
			}
			n.Senao = s
		} else {
			b := p.bloco()
			if b == nil {
				return nil
			}
			n.Senao = b
		}
	}
	return n
}

func (p *Parser) enquanto() *ast.Enquanto {
	pos := p.avancar().Pos
	if _, ok := p.esperar(token.ParenAbre); !ok {
		return nil
	}
	cond := p.expr(pMin)
	if cond == nil {
		return nil
	}
	if _, ok := p.esperar(token.ParenFecha); !ok {
		return nil
	}
	corpo := p.bloco()
	if corpo == nil {
		return nil
	}
	return &ast.Enquanto{Posicao: pos, Cond: cond, Corpo: corpo}
}

func (p *Parser) declFuncao() *ast.DeclFuncao {
	pos := p.avancar().Pos
	nome := p.avancar()
	params, ok := p.parametros()
	if !ok {
		return nil
	}
	corpo := p.bloco()
	if corpo == nil {
		return nil
	}
	return &ast.DeclFuncao{
		Posicao: pos,
		Nome:    &ast.Identificador{Posicao: nome.Pos, Nome: nome.Literal},
		Params:  params,
		Corpo:   corpo,
	}
}

func (p *Parser) parametros() ([]*ast.Identificador, bool) {
	if _, ok := p.esperar(token.ParenAbre); !ok {
		return nil, false
	}
	var params []*ast.Identificador
	if p.atual().Tipo == token.ParenFecha {
		p.avancar()
		return params, true
	}
	for {
		id, ok := p.esperar(token.Ident)
		if !ok {
			return nil, false
		}
		params = append(params, &ast.Identificador{Posicao: id.Pos, Nome: id.Literal})
		if p.atual().Tipo == token.Virgula {
			p.avancar()
			continue
		}
		if _, ok := p.esperar(token.ParenFecha); !ok {
			return nil, false
		}
		return params, true
	}
}

func (p *Parser) bloco() *ast.Bloco {
	abre, ok := p.esperar(token.ChaveAbre)
	if !ok {
		return nil
	}
	b := &ast.Bloco{Posicao: abre.Pos}
	for p.atual().Tipo != token.ChaveFecha && p.atual().Tipo != token.FimArquivo {
		ini := p.i
		if c := p.comando(); c != nil {
			b.Comandos = append(b.Comandos, c)
			continue
		}
		p.sincronizar()
		if p.i == ini {
			p.avancar()
		}
	}
	if _, ok := p.esperar(token.ChaveFecha); !ok {
		return nil
	}
	return b
}

// exprCmd analisa uma expressão seguida de ';' ou de '= valor;' (atribuição).
func (p *Parser) exprCmd() ast.Comando {
	e := p.expr(pMin)
	if e == nil {
		return nil
	}
	if p.atual().Tipo == token.Atribui {
		op := p.avancar()
		switch e.(type) {
		case *ast.Identificador, *ast.Acesso:
		default:
			p.erro(e.Pos(), "alvo de atribuição inválido")
			return nil
		}
		v := p.expr(pMin)
		if v == nil {
			return nil
		}
		if _, ok := p.esperar(token.PontoVirgula); !ok {
			return nil
		}
		return &ast.Atribuicao{Posicao: op.Pos, Alvo: e, Valor: v}
	}
	if _, ok := p.esperar(token.PontoVirgula); !ok {
		return nil
	}
	return &ast.ComandoExpr{Posicao: e.Pos(), Expr: e}
}

// expr é o núcleo do algoritmo de Pratt: analisa um prefixo e depois
// absorve operadores infixos enquanto sua precedência superar prec.
func (p *Parser) expr(prec int) ast.Expressao {
	p.prof++
	defer func() { p.prof-- }()
	if p.prof > profundidadeMax {
		p.erro(p.atual().Pos, "expressão aninhada demais")
		return nil
	}
	esq := p.prefixo()
	if esq == nil {
		return nil
	}
	for prec < precedenciaTok[p.atual().Tipo] {
		if esq = p.infixo(esq); esq == nil {
			return nil
		}
	}
	return esq
}

func (p *Parser) prefixo() ast.Expressao {
	tk := p.atual()
	switch tk.Tipo {
	case token.Ident:
		p.avancar()
		return &ast.Identificador{Posicao: tk.Pos, Nome: tk.Literal}
	case token.Inteiro:
		p.avancar()
		v, err := strconv.ParseInt(tk.Literal, 10, 64)
		if err != nil {
			p.erro(tk.Pos, "inteiro fora do intervalo: %s", tk.Literal)
			return nil
		}
		return &ast.Inteiro{Posicao: tk.Pos, Valor: v}
	case token.Texto:
		p.avancar()
		return &ast.Texto{Posicao: tk.Pos, Valor: tk.Literal}
	case token.Verdadeiro, token.Falso:
		p.avancar()
		return &ast.Booleano{Posicao: tk.Pos, Valor: tk.Tipo == token.Verdadeiro}
	case token.Nao, token.Menos:
		p.avancar()
		dir := p.expr(pPrefixo)
		if dir == nil {
			return nil
		}
		return &ast.Prefixo{Posicao: tk.Pos, Op: tk.Tipo.String(), Dir: dir}
	case token.ParenAbre:
		p.avancar()
		e := p.expr(pMin)
		if e == nil {
			return nil
		}
		if _, ok := p.esperar(token.ParenFecha); !ok {
			return nil
		}
		return e
	case token.ColcheteAbre:
		p.avancar()
		elems, ok := p.lista(token.ColcheteFecha)
		if !ok {
			return nil
		}
		return &ast.ArrayLit{Posicao: tk.Pos, Elementos: elems}
	case token.Fn:
		p.avancar()
		params, ok := p.parametros()
		if !ok {
			return nil
		}
		corpo := p.bloco()
		if corpo == nil {
			return nil
		}
		return &ast.LiteralFuncao{Posicao: tk.Pos, Params: params, Corpo: corpo}
	case token.Ilegal:
		p.erro(tk.Pos, "%s", tk.Literal)
		return nil
	}
	p.erro(tk.Pos, "expressão esperada, encontrado %s", descrever(tk))
	return nil
}

func (p *Parser) infixo(esq ast.Expressao) ast.Expressao {
	op := p.avancar()
	switch op.Tipo {
	case token.ParenAbre:
		args, ok := p.lista(token.ParenFecha)
		if !ok {
			return nil
		}
		return &ast.Chamada{Posicao: op.Pos, Funcao: esq, Args: args}
	case token.ColcheteAbre:
		idx := p.expr(pMin)
		if idx == nil {
			return nil
		}
		if _, ok := p.esperar(token.ColcheteFecha); !ok {
			return nil
		}
		return &ast.Acesso{Posicao: op.Pos, Alvo: esq, Indice: idx}
	}
	dir := p.expr(precedenciaTok[op.Tipo])
	if dir == nil {
		return nil
	}
	return &ast.Infixo{Posicao: op.Pos, Op: op.Tipo.String(), Esq: esq, Dir: dir}
}

// lista analisa expressões separadas por vírgula até o token fim.
func (p *Parser) lista(fim token.Tipo) ([]ast.Expressao, bool) {
	var res []ast.Expressao
	if p.atual().Tipo == fim {
		p.avancar()
		return res, true
	}
	for {
		e := p.expr(pMin)
		if e == nil {
			return nil, false
		}
		res = append(res, e)
		if p.atual().Tipo == token.Virgula {
			p.avancar()
			continue
		}
		if _, ok := p.esperar(fim); !ok {
			return nil, false
		}
		return res, true
	}
}
