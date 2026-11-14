// Pacote parser implementa o tokenizador e o analisador de uma linguagem
// de comandos de chave-valor:
//
//	SET <chave> <valor>
//	GET <chave>
//	DEL <chave>
//	SCAN [<prefixo>] [LIMIT <n>]
//	BEGIN | COMMIT | ROLLBACK
//
// Os nomes dos comandos não diferenciam maiúsculas de minúsculas. Chaves e
// valores são palavras soltas ou textos entre aspas duplas, com os escapes
// \" \\ \n \t \r. Uma palavra LIMIT sem aspas é a palavra-chave; entre
// aspas é um prefixo comum.
package parser

import (
	"fmt"
	"strconv"
	"strings"
)

// Tipo identifica o comando.
type Tipo int

const (
	Set Tipo = iota + 1
	Get
	Del
	Scan
	Begin
	Commit
	Rollback
)

func (t Tipo) String() string {
	switch t {
	case Set:
		return "SET"
	case Get:
		return "GET"
	case Del:
		return "DEL"
	case Scan:
		return "SCAN"
	case Begin:
		return "BEGIN"
	case Commit:
		return "COMMIT"
	case Rollback:
		return "ROLLBACK"
	}
	return "?"
}

// Comando é o resultado da análise.
type Comando struct {
	Tipo    Tipo
	Chave   string
	Valor   string
	Prefixo string
	Limite  int // 0 = sem limite (apenas SCAN)
}

// ErroSintaxe descreve um problema com a posição (em bytes) onde ocorreu.
type ErroSintaxe struct {
	Pos int
	Msg string
}

func (e *ErroSintaxe) Error() string {
	return fmt.Sprintf("erro de sintaxe na posição %d: %s", e.Pos, e.Msg)
}

// Token é um pedaço da entrada.
type Token struct {
	Valor string
	Pos   int
	Aspas bool // veio entre aspas: nunca é palavra-chave
}

func eEspaco(c byte) bool { return c == ' ' || c == '\t' || c == '\n' || c == '\r' }

// Tokenizar divide a linha em tokens.
func Tokenizar(s string) ([]Token, error) {
	var toks []Token
	i := 0
	for i < len(s) {
		if eEspaco(s[i]) {
			i++
			continue
		}
		ini := i
		if s[i] == '"' {
			var sb strings.Builder
			i++
			fechou := false
			for i < len(s) {
				c := s[i]
				if c == '\\' {
					if i+1 >= len(s) {
						return nil, &ErroSintaxe{i, "escape incompleto"}
					}
					switch s[i+1] {
					case '"', '\\':
						sb.WriteByte(s[i+1])
					case 'n':
						sb.WriteByte('\n')
					case 't':
						sb.WriteByte('\t')
					case 'r':
						sb.WriteByte('\r')
					default:
						return nil, &ErroSintaxe{i, fmt.Sprintf("escape desconhecido \\%c", s[i+1])}
					}
					i += 2
					continue
				}
				if c == '"' {
					fechou = true
					i++
					break
				}
				sb.WriteByte(c)
				i++
			}
			if !fechou {
				return nil, &ErroSintaxe{ini, "aspas não fechadas"}
			}
			if i < len(s) && !eEspaco(s[i]) {
				return nil, &ErroSintaxe{i, "esperado espaço depois das aspas"}
			}
			toks = append(toks, Token{Valor: sb.String(), Pos: ini, Aspas: true})
			continue
		}
		for i < len(s) && !eEspaco(s[i]) {
			if s[i] == '"' {
				return nil, &ErroSintaxe{i, "aspas no meio de uma palavra"}
			}
			i++
		}
		toks = append(toks, Token{Valor: s[ini:i], Pos: ini})
	}
	return toks, nil
}

// Analisar converte uma linha em Comando.
func Analisar(linha string) (Comando, error) {
	toks, err := Tokenizar(linha)
	if err != nil {
		return Comando{}, err
	}
	if len(toks) == 0 {
		return Comando{}, &ErroSintaxe{0, "comando vazio"}
	}
	nome := strings.ToUpper(toks[0].Valor)
	args := toks[1:]

	exato := func(n int, uso string) error {
		if len(args) < n {
			return &ErroSintaxe{len(linha), "faltam argumentos; uso: " + uso}
		}
		if len(args) > n {
			return &ErroSintaxe{args[n].Pos, "argumento a mais; uso: " + uso}
		}
		return nil
	}

	switch nome {
	case "SET":
		if err := exato(2, "SET chave valor"); err != nil {
			return Comando{}, err
		}
		return Comando{Tipo: Set, Chave: args[0].Valor, Valor: args[1].Valor}, nil
	case "GET", "DEL":
		if err := exato(1, nome+" chave"); err != nil {
			return Comando{}, err
		}
		t := Get
		if nome == "DEL" {
			t = Del
		}
		return Comando{Tipo: t, Chave: args[0].Valor}, nil
	case "BEGIN", "COMMIT", "ROLLBACK":
		if err := exato(0, nome); err != nil {
			return Comando{}, err
		}
		return Comando{Tipo: map[string]Tipo{"BEGIN": Begin, "COMMIT": Commit, "ROLLBACK": Rollback}[nome]}, nil
	case "SCAN":
		return analisarScan(args, linha)
	}
	return Comando{}, &ErroSintaxe{toks[0].Pos, fmt.Sprintf("comando desconhecido %q", toks[0].Valor)}
}

func ehLimit(t Token) bool { return !t.Aspas && strings.EqualFold(t.Valor, "LIMIT") }

func analisarScan(args []Token, linha string) (Comando, error) {
	c := Comando{Tipo: Scan}
	const uso = "SCAN [prefixo] [LIMIT n]"
	if len(args) > 0 && !ehLimit(args[0]) {
		c.Prefixo = args[0].Valor
		args = args[1:]
	}
	if len(args) == 0 {
		return c, nil
	}
	if !ehLimit(args[0]) {
		return Comando{}, &ErroSintaxe{args[0].Pos, "esperado LIMIT; uso: " + uso}
	}
	if len(args) < 2 {
		return Comando{}, &ErroSintaxe{len(linha), "LIMIT precisa de um número; uso: " + uso}
	}
	n, err := strconv.Atoi(args[1].Valor)
	if err != nil || n < 1 {
		return Comando{}, &ErroSintaxe{args[1].Pos, "LIMIT deve ser um inteiro positivo"}
	}
	if len(args) > 2 {
		return Comando{}, &ErroSintaxe{args[2].Pos, "argumento a mais; uso: " + uso}
	}
	c.Limite = n
	return c, nil
}
