// Pacote token define os tokens da linguagem Mini, as posições no código
// fonte e o tipo de erro com posição usado por todas as fases.
package token

import "fmt"

// Tipo identifica a categoria de um token.
type Tipo int

const (
	Ilegal Tipo = iota
	FimArquivo
	Ident
	Inteiro
	Texto

	Atribui
	Mais
	Menos
	Asterisco
	Barra
	Resto
	Nao
	Igual
	Diferente
	Menor
	MenorIgual
	Maior
	MaiorIgual
	E
	Ou

	Virgula
	PontoVirgula
	ParenAbre
	ParenFecha
	ChaveAbre
	ChaveFecha
	ColcheteAbre
	ColcheteFecha

	Let
	Fn
	Se
	Senao
	Enquanto
	Retorna
	Verdadeiro
	Falso
)

var nomes = [...]string{
	Ilegal: "ILEGAL", FimArquivo: "FIM", Ident: "IDENT", Inteiro: "INTEIRO", Texto: "TEXTO",
	Atribui: "=", Mais: "+", Menos: "-", Asterisco: "*", Barra: "/", Resto: "%",
	Nao: "!", Igual: "==", Diferente: "!=", Menor: "<", MenorIgual: "<=",
	Maior: ">", MaiorIgual: ">=", E: "&&", Ou: "||",
	Virgula: ",", PontoVirgula: ";", ParenAbre: "(", ParenFecha: ")",
	ChaveAbre: "{", ChaveFecha: "}", ColcheteAbre: "[", ColcheteFecha: "]",
	Let: "let", Fn: "fn", Se: "if", Senao: "else", Enquanto: "while",
	Retorna: "return", Verdadeiro: "true", Falso: "false",
}

func (t Tipo) String() string {
	if int(t) < 0 || int(t) >= len(nomes) {
		return fmt.Sprintf("Tipo(%d)", int(t))
	}
	return nomes[t]
}

var palavrasChave = map[string]Tipo{
	"let": Let, "fn": Fn, "if": Se, "else": Senao, "while": Enquanto,
	"return": Retorna, "true": Verdadeiro, "false": Falso,
}

// BuscarIdent devolve o tipo de palavra-chave de s, ou Ident se não for uma.
func BuscarIdent(s string) Tipo {
	if t, ok := palavrasChave[s]; ok {
		return t
	}
	return Ident
}

// Posicao indica um ponto do código fonte. Linha e Coluna começam em 1 e a
// coluna conta caracteres (runas); Deslocamento conta bytes desde o início.
type Posicao struct {
	Linha        int
	Coluna       int
	Deslocamento int
}

func (p Posicao) String() string { return fmt.Sprintf("%d:%d", p.Linha, p.Coluna) }

// Valida informa se a posição foi preenchida.
func (p Posicao) Valida() bool { return p.Linha > 0 }

// Token é uma unidade léxica com seu texto e posição.
type Token struct {
	Tipo    Tipo
	Literal string
	Pos     Posicao
}

func (t Token) String() string { return fmt.Sprintf("%s(%q)@%s", t.Tipo, t.Literal, t.Pos) }

// Erro é um erro associado a uma posição do fonte. Todas as fases do
// pipeline (parser, semântica, tipos, execução) o utilizam.
type Erro struct {
	Posicao Posicao
	Msg     string
}

func (e *Erro) Error() string {
	if !e.Posicao.Valida() {
		return e.Msg
	}
	return fmt.Sprintf("%s: %s", e.Posicao, e.Msg)
}

// Pos devolve a posição do erro.
func (e *Erro) Pos() Posicao { return e.Posicao }

// Mensagem devolve o texto do erro sem o prefixo de posição.
func (e *Erro) Mensagem() string { return e.Msg }

// Errorf cria um *Erro formatando a mensagem.
func Errorf(pos Posicao, formato string, args ...any) *Erro {
	return &Erro{Posicao: pos, Msg: fmt.Sprintf(formato, args...)}
}
