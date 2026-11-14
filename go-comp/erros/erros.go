// Pacote erros coleta diagnósticos de todas as fases e os apresenta com
// linha, coluna e um trecho do código fonte apontando o ponto do problema.
package erros

import (
	"errors"
	"fmt"
	"strings"

	"greenout/comp/token"
)

// Fase identifica a etapa do pipeline que produziu o diagnóstico.
type Fase string

const (
	Sintaxe    Fase = "sintaxe"
	Semantica  Fase = "semântica"
	Tipos      Fase = "tipos"
	Compilacao Fase = "compilação"
	Execucao   Fase = "execução"
)

// Item é um diagnóstico. Pos pode ser inválida (sem localização).
type Item struct {
	Fase  Fase
	Pos   token.Posicao
	Msg   string
	Aviso bool
}

// Coletor acumula diagnósticos sobre um fonte.
type Coletor struct {
	// Limite é o máximo de itens exibidos por Formatar (0 = sem limite).
	Limite int
	linhas []string
	itens  []Item
}

// Novo cria um coletor para o fonte, usado para extrair os trechos.
func Novo(fonte string) *Coletor {
	return &Coletor{linhas: strings.Split(strings.ReplaceAll(fonte, "\r\n", "\n"), "\n")}
}

// Adicionar registra um erro.
func (c *Coletor) Adicionar(fase Fase, pos token.Posicao, msg string) {
	c.itens = append(c.itens, Item{Fase: fase, Pos: pos, Msg: msg})
}

// AdicionarAviso registra um aviso (não conta como erro).
func (c *Coletor) AdicionarAviso(fase Fase, pos token.Posicao, msg string) {
	c.itens = append(c.itens, Item{Fase: fase, Pos: pos, Msg: msg, Aviso: true})
}

// AdicionarErro registra um error qualquer; se for (ou embrulhar) um
// *token.Erro, aproveita posição e mensagem.
func (c *Coletor) AdicionarErro(fase Fase, err error) {
	if err == nil {
		return
	}
	var te *token.Erro
	if errors.As(err, &te) {
		c.Adicionar(fase, te.Posicao, te.Msg)
		return
	}
	c.Adicionar(fase, token.Posicao{}, err.Error())
}

// AdicionarTodos registra uma lista de erros de uma mesma fase.
func (c *Coletor) AdicionarTodos(fase Fase, es []*token.Erro) {
	for _, e := range es {
		c.Adicionar(fase, e.Posicao, e.Msg)
	}
}

// AdicionarAvisos registra uma lista de avisos de uma mesma fase.
func (c *Coletor) AdicionarAvisos(fase Fase, es []*token.Erro) {
	for _, e := range es {
		c.AdicionarAviso(fase, e.Posicao, e.Msg)
	}
}

// Itens devolve os diagnósticos na ordem de registro.
func (c *Coletor) Itens() []Item { return c.itens }

// Contagem devolve quantos erros e quantos avisos foram registrados.
func (c *Coletor) Contagem() (erros, avisos int) {
	for _, it := range c.itens {
		if it.Aviso {
			avisos++
		} else {
			erros++
		}
	}
	return
}

// TemErros informa se há algum erro (avisos não contam).
func (c *Coletor) TemErros() bool {
	e, _ := c.Contagem()
	return e > 0
}

// Linha devolve o texto da linha (1-based) do fonte, sem quebra de linha.
func (c *Coletor) Linha(n int) (string, bool) {
	if n < 1 || n > len(c.linhas) {
		return "", false
	}
	return c.linhas[n-1], true
}

// Trecho devolve a linha do fonte seguida de uma linha com ^ sob a coluna,
// ou "" se a posição não existir no fonte. Tabulações são preservadas no
// recuo para que o ^ fique alinhado.
func (c *Coletor) Trecho(pos token.Posicao) string {
	if !pos.Valida() {
		return ""
	}
	linha, ok := c.Linha(pos.Linha)
	if !ok {
		return ""
	}
	num := fmt.Sprint(pos.Linha)
	margem := strings.Repeat(" ", len(num))
	var recuo strings.Builder
	col := 1
	for _, r := range linha {
		if col >= pos.Coluna {
			break
		}
		if r == '\t' {
			recuo.WriteRune('\t')
		} else {
			recuo.WriteRune(' ')
		}
		col++
	}
	for ; col < pos.Coluna; col++ { // coluna além do fim da linha (ex.: fim do arquivo)
		recuo.WriteRune(' ')
	}
	return fmt.Sprintf("%s |\n%s | %s\n%s | %s^", margem, num, linha, margem, recuo.String())
}

// Formatar produz o relatório completo de diagnósticos.
func (c *Coletor) Formatar() string {
	if len(c.itens) == 0 {
		return ""
	}
	var sb strings.Builder
	exibidos := c.itens
	omitidos := 0
	if c.Limite > 0 && len(exibidos) > c.Limite {
		omitidos = len(exibidos) - c.Limite
		exibidos = exibidos[:c.Limite]
	}
	for _, it := range exibidos {
		tipo := "erro"
		if it.Aviso {
			tipo = "aviso"
		}
		fmt.Fprintf(&sb, "%s[%s]: %s\n", tipo, it.Fase, it.Msg)
		if it.Pos.Valida() {
			fmt.Fprintf(&sb, " --> %s\n", it.Pos)
			if t := c.Trecho(it.Pos); t != "" {
				sb.WriteString(t + "\n")
			}
		}
		sb.WriteString("\n")
	}
	if omitidos > 0 {
		fmt.Fprintf(&sb, "... e mais %d diagnóstico(s)\n", omitidos)
	}
	e, a := c.Contagem()
	fmt.Fprintf(&sb, "%d erro(s), %d aviso(s)\n", e, a)
	return sb.String()
}
