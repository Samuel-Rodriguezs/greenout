// Pacote repl implementa o laço interativo de Mini sobre io.Reader e
// io.Writer, o que o torna testável sem terminal. O estado (variáveis e
// funções) persiste entre as linhas digitadas.
package repl

import (
	"bufio"
	"fmt"
	"io"
	"strings"

	"greenout/comp/codigo"
	"greenout/comp/compilador"
	"greenout/comp/erros"
	"greenout/comp/impressor"
	"greenout/comp/interp"
	"greenout/comp/lexer"
	"greenout/comp/padrao"
	"greenout/comp/parser"
	"greenout/comp/token"
)

// Textos dos prompts.
const (
	Prompt      = ">> "
	Continuacao = "... "
	textoAjuda  = "comandos:\n  :ajuda          mostra esta ajuda\n  :limpar         esquece variáveis e funções\n  :fmt <código>   mostra o código formatado\n  :asm <código>   mostra o bytecode compilado\n  :sair           encerra\n"
)

// Sessao guarda o estado de um REPL.
type Sessao struct {
	in    *interp.Interp
	saida io.Writer
}

// NovaSessao cria uma sessão cujo print escreve em saida.
func NovaSessao(saida io.Writer) *Sessao {
	s := &Sessao{saida: saida}
	s.reiniciar()
	return s
}

func (s *Sessao) reiniciar() {
	s.in = interp.Novo()
	padrao.Instalar(s.in, s.saida)
}

// Incompleta informa se o fonte tem delimitadores abertos e precisa de mais linhas.
func Incompleta(fonte string) bool {
	prof := 0
	for _, t := range lexer.Tokens(fonte) {
		switch t.Tipo {
		case token.ParenAbre, token.ChaveAbre, token.ColcheteAbre:
			prof++
		case token.ParenFecha, token.ChaveFecha, token.ColcheteFecha:
			prof--
		}
	}
	return prof > 0
}

// normalizar acrescenta o ';' final quando o usuário o omitiu.
func normalizar(fonte string) string {
	t := strings.TrimRight(fonte, " \t\r\n")
	if t == "" || strings.HasSuffix(t, ";") || strings.HasSuffix(t, "}") {
		return t
	}
	return t + ";"
}

// Avaliar executa um trecho e devolve o valor a exibir (vazio para nulo) e os
// diagnósticos formatados (vazio se não houve erro).
func (s *Sessao) Avaliar(fonte string) (valor, diagnostico string) {
	fonte = normalizar(fonte)
	col := erros.Novo(fonte)
	prog, es := parser.Analisar(fonte)
	if len(es) > 0 {
		col.AdicionarTodos(erros.Sintaxe, es)
		return "", col.Formatar()
	}
	v, err := s.in.Executar(prog)
	if err != nil {
		col.AdicionarErro(erros.Execucao, err)
		return "", col.Formatar()
	}
	if _, nulo := v.(interp.Nulo); nulo {
		return "", ""
	}
	return interp.Repr(v), ""
}

// comando trata as linhas que começam com ':'. O segundo resultado indica
// que o REPL deve encerrar.
func (s *Sessao) comando(linha string) (sair bool) {
	nome, resto, _ := strings.Cut(linha, " ")
	switch nome {
	case ":sair", ":q":
		return true
	case ":ajuda":
		fmt.Fprint(s.saida, textoAjuda)
	case ":limpar":
		s.reiniciar()
		fmt.Fprintln(s.saida, "estado limpo")
	case ":fmt":
		s.formatar(resto)
	case ":asm":
		s.desmontar(resto)
	default:
		fmt.Fprintf(s.saida, "comando desconhecido %q (use :ajuda)\n", nome)
	}
	return false
}

func (s *Sessao) formatar(fonte string) {
	fonte = normalizar(fonte)
	prog, es := parser.Analisar(fonte)
	if len(es) > 0 {
		col := erros.Novo(fonte)
		col.AdicionarTodos(erros.Sintaxe, es)
		fmt.Fprint(s.saida, col.Formatar())
		return
	}
	fmt.Fprint(s.saida, impressor.Formatar(prog))
}

func (s *Sessao) desmontar(fonte string) {
	fonte = normalizar(fonte)
	col := erros.Novo(fonte)
	prog, es := parser.Analisar(fonte)
	if len(es) > 0 {
		col.AdicionarTodos(erros.Sintaxe, es)
		fmt.Fprint(s.saida, col.Formatar())
		return
	}
	p, err := compilador.Compilar(prog, padrao.Nomes())
	if err != nil {
		col.AdicionarErro(erros.Compilacao, err)
		fmt.Fprint(s.saida, col.Formatar())
		return
	}
	fmt.Fprint(s.saida, codigo.Desmontar(p))
}

// Executar lê linhas de entrada até EOF ou ":sair". Entradas com
// delimitadores abertos continuam na linha seguinte.
func Executar(entrada io.Reader, saida io.Writer) error {
	s := NovaSessao(saida)
	sc := bufio.NewScanner(entrada)
	sc.Buffer(make([]byte, 0, 64*1024), 1024*1024)
	var buf strings.Builder
	fmt.Fprint(saida, Prompt)
	for sc.Scan() {
		linha := sc.Text()
		if buf.Len() == 0 && strings.HasPrefix(strings.TrimSpace(linha), ":") {
			if s.comando(strings.TrimSpace(linha)) {
				return nil
			}
			fmt.Fprint(saida, Prompt)
			continue
		}
		buf.WriteString(linha)
		buf.WriteString("\n")
		if Incompleta(buf.String()) {
			fmt.Fprint(saida, Continuacao)
			continue
		}
		s.executarBuffer(buf.String())
		buf.Reset()
		fmt.Fprint(saida, Prompt)
	}
	if buf.Len() > 0 { // entrada terminou no meio de um bloco
		s.executarBuffer(buf.String())
	}
	return sc.Err()
}

func (s *Sessao) executarBuffer(fonte string) {
	if strings.TrimSpace(fonte) == "" {
		return
	}
	valor, diag := s.Avaliar(fonte)
	if diag != "" {
		fmt.Fprint(s.saida, diag)
	} else if valor != "" {
		fmt.Fprintln(s.saida, valor)
	}
}
