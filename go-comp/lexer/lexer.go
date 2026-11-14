// Pacote lexer converte o código fonte Mini em uma sequência de tokens.
package lexer

import (
	"strings"
	"unicode/utf8"

	"greenout/comp/token"
)

// Lexer percorre o fonte rastreando linha e coluna.
type Lexer struct {
	fonte  string
	pos    int
	linha  int
	coluna int
}

// Novo cria um lexer para o fonte dado.
func Novo(fonte string) *Lexer {
	return &Lexer{fonte: fonte, linha: 1, coluna: 1}
}

// Tokens devolve todos os tokens do fonte, terminando com FimArquivo.
func Tokens(fonte string) []token.Token {
	l := Novo(fonte)
	var res []token.Token
	for {
		t := l.Proximo()
		res = append(res, t)
		if t.Tipo == token.FimArquivo {
			return res
		}
	}
}

func (l *Lexer) fim() bool { return l.pos >= len(l.fonte) }

func (l *Lexer) olhar() byte {
	if l.fim() {
		return 0
	}
	return l.fonte[l.pos]
}

func (l *Lexer) olharSeguinte() byte {
	if l.pos+1 >= len(l.fonte) {
		return 0
	}
	return l.fonte[l.pos+1]
}

// avancar consome um byte, atualizando linha e coluna. Bytes de
// continuação UTF-8 não avançam a coluna, que conta runas.
func (l *Lexer) avancar() {
	c := l.fonte[l.pos]
	l.pos++
	switch {
	case c == '\n':
		l.linha++
		l.coluna = 1
	case c&0xC0 != 0x80:
		l.coluna++
	}
}

func (l *Lexer) posicao() token.Posicao {
	return token.Posicao{Linha: l.linha, Coluna: l.coluna, Deslocamento: l.pos}
}

func letra(c byte) bool  { return c == '_' || c >= 'a' && c <= 'z' || c >= 'A' && c <= 'Z' }
func digito(c byte) bool { return c >= '0' && c <= '9' }

// pularBrancos ignora espaços e comentários de linha (// ...).
func (l *Lexer) pularBrancos() {
	for !l.fim() {
		c := l.olhar()
		switch {
		case c == ' ' || c == '\t' || c == '\r' || c == '\n':
			l.avancar()
		case c == '/' && l.olharSeguinte() == '/':
			for !l.fim() && l.olhar() != '\n' {
				l.avancar()
			}
		default:
			return
		}
	}
}

// Proximo devolve o próximo token. Após o fim devolve FimArquivo sempre.
func (l *Lexer) Proximo() token.Token {
	l.pularBrancos()
	pos := l.posicao()
	if l.fim() {
		return token.Token{Tipo: token.FimArquivo, Pos: pos}
	}
	c := l.olhar()
	switch {
	case letra(c):
		ini := l.pos
		for !l.fim() && (letra(l.olhar()) || digito(l.olhar())) {
			l.avancar()
		}
		lit := l.fonte[ini:l.pos]
		return token.Token{Tipo: token.BuscarIdent(lit), Literal: lit, Pos: pos}
	case digito(c):
		ini := l.pos
		for !l.fim() && digito(l.olhar()) {
			l.avancar()
		}
		if !l.fim() && letra(l.olhar()) {
			for !l.fim() && (letra(l.olhar()) || digito(l.olhar())) {
				l.avancar()
			}
			return token.Token{Tipo: token.Ilegal, Literal: "número inválido " + l.fonte[ini:l.pos], Pos: pos}
		}
		return token.Token{Tipo: token.Inteiro, Literal: l.fonte[ini:l.pos], Pos: pos}
	case c == '"':
		return l.lerTexto(pos)
	}
	return l.operador(pos)
}

var simples = map[byte]token.Tipo{
	'+': token.Mais, '-': token.Menos, '*': token.Asterisco, '/': token.Barra, '%': token.Resto,
	',': token.Virgula, ';': token.PontoVirgula, '(': token.ParenAbre, ')': token.ParenFecha,
	'{': token.ChaveAbre, '}': token.ChaveFecha, '[': token.ColcheteAbre, ']': token.ColcheteFecha,
}

// operador reconhece operadores de um ou dois caracteres.
func (l *Lexer) operador(pos token.Posicao) token.Token {
	c := l.olhar()
	prox := l.olharSeguinte()
	dois := func(t token.Tipo) token.Token {
		lit := l.fonte[l.pos : l.pos+2]
		l.avancar()
		l.avancar()
		return token.Token{Tipo: t, Literal: lit, Pos: pos}
	}
	um := func(t token.Tipo) token.Token {
		lit := l.fonte[l.pos : l.pos+1]
		l.avancar()
		return token.Token{Tipo: t, Literal: lit, Pos: pos}
	}
	switch {
	case c == '=' && prox == '=':
		return dois(token.Igual)
	case c == '=':
		return um(token.Atribui)
	case c == '!' && prox == '=':
		return dois(token.Diferente)
	case c == '!':
		return um(token.Nao)
	case c == '<' && prox == '=':
		return dois(token.MenorIgual)
	case c == '<':
		return um(token.Menor)
	case c == '>' && prox == '=':
		return dois(token.MaiorIgual)
	case c == '>':
		return um(token.Maior)
	case c == '&' && prox == '&':
		return dois(token.E)
	case c == '|' && prox == '|':
		return dois(token.Ou)
	}
	if t, ok := simples[c]; ok {
		return um(t)
	}
	r, tam := utf8.DecodeRuneInString(l.fonte[l.pos:])
	for i := 0; i < tam; i++ {
		l.avancar()
	}
	msg := "caractere inesperado " + aspas(r)
	if c == '&' || c == '|' {
		msg += " (use '" + string(r) + string(r) + "')"
	}
	return token.Token{Tipo: token.Ilegal, Literal: msg, Pos: pos}
}

func aspas(r rune) string { return "'" + string(r) + "'" }

// lerTexto lê um literal entre aspas com escapes \n \t \r \" \\.
// Em caso de erro devolve um token Ilegal cujo Literal descreve o problema.
func (l *Lexer) lerTexto(pos token.Posicao) token.Token {
	l.avancar() // aspas de abertura
	var sb strings.Builder
	erro := ""
	for {
		if l.fim() || l.olhar() == '\n' {
			return token.Token{Tipo: token.Ilegal, Literal: "texto não terminado", Pos: pos}
		}
		c := l.olhar()
		if c == '"' {
			l.avancar()
			break
		}
		if c != '\\' {
			sb.WriteByte(c)
			l.avancar()
			continue
		}
		l.avancar()
		if l.fim() || l.olhar() == '\n' {
			return token.Token{Tipo: token.Ilegal, Literal: "texto não terminado", Pos: pos}
		}
		e := l.olhar()
		l.avancar()
		switch e {
		case 'n':
			sb.WriteByte('\n')
		case 't':
			sb.WriteByte('\t')
		case 'r':
			sb.WriteByte('\r')
		case '"':
			sb.WriteByte('"')
		case '\\':
			sb.WriteByte('\\')
		default:
			if erro == "" {
				erro = "escape inválido '\\" + string(e) + "'"
			}
		}
	}
	if erro != "" {
		return token.Token{Tipo: token.Ilegal, Literal: erro, Pos: pos}
	}
	return token.Token{Tipo: token.Texto, Literal: sb.String(), Pos: pos}
}
