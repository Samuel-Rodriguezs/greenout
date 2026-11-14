// Pacote grep implementa uma versão simplificada do utilitário Unix grep.
package grep

import (
	"errors"
	"fmt"
	"io"
	"regexp"
	"strings"
)

// ErrSemCorrespondencia indica que nenhuma linha casou (status 1 no grep real).
var ErrSemCorrespondencia = errors.New("grep: nenhuma linha correspondente")

// Opcoes controla o comportamento da busca.
type Opcoes struct {
	IgnorarCaixa bool // -i
	Inverter     bool // -v
	Numerar      bool // -n
	Contar       bool // -c
	Literal      bool // -F
}

// Compilar converte o padrão em expressão regular conforme as opções.
func Compilar(padrao string, o Opcoes) (*regexp.Regexp, error) {
	if o.Literal {
		padrao = regexp.QuoteMeta(padrao)
	}
	if o.IgnorarCaixa {
		padrao = "(?i)" + padrao
	}
	re, err := regexp.Compile(padrao)
	if err != nil {
		return nil, fmt.Errorf("grep: padrão inválido: %w", err)
	}
	return re, nil
}

// Casar devolve os índices (base 1) das linhas selecionadas.
func Casar(linhas []string, re *regexp.Regexp, inverter bool) []int {
	var idx []int
	for i, l := range linhas {
		if re.MatchString(l) != inverter {
			idx = append(idx, i+1)
		}
	}
	return idx
}

// Executar interpreta [-ivncF] PADRÃO e filtra a entrada.
func Executar(args []string, in io.Reader, out io.Writer) error {
	var o Opcoes
	var restante []string
	for i, a := range args {
		if a == "--" {
			restante = args[i+1:]
			break
		}
		if len(a) > 1 && a[0] == '-' {
			for _, f := range a[1:] {
				switch f {
				case 'i':
					o.IgnorarCaixa = true
				case 'v':
					o.Inverter = true
				case 'n':
					o.Numerar = true
				case 'c':
					o.Contar = true
				case 'F':
					o.Literal = true
				default:
					return fmt.Errorf("grep: opção inválida -%c", f)
				}
			}
			continue
		}
		restante = args[i:]
		break
	}
	if len(restante) != 1 {
		return errors.New("grep: uso: grep [-ivncF] PADRÃO")
	}
	re, err := Compilar(restante[0], o)
	if err != nil {
		return err
	}
	dados, err := io.ReadAll(in)
	if err != nil {
		return err
	}
	var linhas []string
	if len(dados) > 0 {
		linhas = strings.Split(strings.TrimSuffix(string(dados), "\n"), "\n")
	}
	idx := Casar(linhas, re, o.Inverter)
	if o.Contar {
		fmt.Fprintln(out, len(idx))
	} else {
		for _, n := range idx {
			if o.Numerar {
				fmt.Fprintf(out, "%d:", n)
			}
			fmt.Fprintln(out, linhas[n-1])
		}
	}
	if len(idx) == 0 {
		return ErrSemCorrespondencia
	}
	return nil
}
