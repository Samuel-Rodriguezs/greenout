// Pacote head implementa uma versão simplificada do utilitário Unix head.
package head

import (
	"fmt"
	"io"
	"strconv"
	"strings"
)

// Primeiras devolve as n primeiras linhas. Se n for negativo, devolve todas
// menos as últimas |n| linhas.
func Primeiras(linhas []string, n int) []string {
	if n < 0 {
		n = len(linhas) + n
	}
	if n < 0 {
		n = 0
	}
	if n > len(linhas) {
		n = len(linhas)
	}
	return linhas[:n]
}

// ParseN interpreta os argumentos "-n N", "-nN" ou "-N"; o padrão é 10.
func ParseN(args []string) (int, error) {
	n := 10
	for i := 0; i < len(args); i++ {
		a := args[i]
		var v string
		switch {
		case a == "-n":
			if i+1 >= len(args) {
				return 0, fmt.Errorf("head: -n requer um valor")
			}
			i++
			v = args[i]
		case strings.HasPrefix(a, "-n"):
			v = a[2:]
		case len(a) > 1 && a[0] == '-' && a[1] >= '0' && a[1] <= '9':
			v = a[1:]
		default:
			return 0, fmt.Errorf("head: argumento inválido %q", a)
		}
		x, err := strconv.Atoi(v)
		if err != nil {
			return 0, fmt.Errorf("head: número de linhas inválido %q", v)
		}
		n = x
	}
	return n, nil
}

// Executar escreve as primeiras linhas da entrada.
func Executar(args []string, in io.Reader, out io.Writer) error {
	n, err := ParseN(args)
	if err != nil {
		return err
	}
	dados, err := io.ReadAll(in)
	if err != nil {
		return err
	}
	if len(dados) == 0 {
		return nil
	}
	linhas := strings.Split(strings.TrimSuffix(string(dados), "\n"), "\n")
	for _, l := range Primeiras(linhas, n) {
		if _, err := fmt.Fprintln(out, l); err != nil {
			return err
		}
	}
	return nil
}
