// Pacote nl implementa uma versão simplificada do utilitário Unix nl.
package nl

import (
	"fmt"
	"io"
	"strconv"
	"strings"
)

// Opcoes controla a numeração.
type Opcoes struct {
	TodasLinhas bool   // -b a: numera também as linhas em branco (padrão: -b t)
	Largura     int    // -w: largura do número
	Separador   string // -s: texto entre o número e a linha
	Inicio      int    // -v: primeiro número
}

// PadraoOpcoes devolve os valores padrão do nl.
func PadraoOpcoes() Opcoes {
	return Opcoes{Largura: 6, Separador: "\t", Inicio: 1}
}

// Numerar prefixa cada linha com seu número. Linhas em branco não numeradas
// recebem apenas espaços para manter o alinhamento.
func Numerar(linhas []string, o Opcoes) []string {
	res := make([]string, 0, len(linhas))
	n := o.Inicio
	for _, l := range linhas {
		if l == "" && !o.TodasLinhas {
			res = append(res, strings.Repeat(" ", o.Largura)+o.Separador)
			continue
		}
		res = append(res, fmt.Sprintf("%*d%s%s", o.Largura, n, o.Separador, l))
		n++
	}
	return res
}

// Executar interpreta [-b a|t] [-w N] [-s SEP] [-v N].
func Executar(args []string, in io.Reader, out io.Writer) error {
	o := PadraoOpcoes()
	for i := 0; i < len(args); i++ {
		if i+1 >= len(args) {
			return fmt.Errorf("nl: opção %q requer um valor", args[i])
		}
		v := args[i+1]
		switch args[i] {
		case "-b":
			switch v {
			case "a":
				o.TodasLinhas = true
			case "t":
				o.TodasLinhas = false
			default:
				return fmt.Errorf("nl: estilo de numeração inválido %q", v)
			}
		case "-w":
			n, err := strconv.Atoi(v)
			if err != nil || n < 1 {
				return fmt.Errorf("nl: largura inválida %q", v)
			}
			o.Largura = n
		case "-s":
			o.Separador = v
		case "-v":
			n, err := strconv.Atoi(v)
			if err != nil {
				return fmt.Errorf("nl: número inicial inválido %q", v)
			}
			o.Inicio = n
		default:
			return fmt.Errorf("nl: opção inválida %q", args[i])
		}
		i++
	}
	dados, err := io.ReadAll(in)
	if err != nil {
		return err
	}
	if len(dados) == 0 {
		return nil
	}
	linhas := strings.Split(strings.TrimSuffix(string(dados), "\n"), "\n")
	for _, l := range Numerar(linhas, o) {
		if _, err := fmt.Fprintln(out, l); err != nil {
			return err
		}
	}
	return nil
}
