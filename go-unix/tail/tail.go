// Pacote tail implementa uma versão simplificada do utilitário Unix tail.
package tail

import (
	"fmt"
	"io"
	"strconv"
	"strings"
)

// Ultimas devolve as n últimas linhas.
func Ultimas(linhas []string, n int) []string {
	if n < 0 {
		n = 0
	}
	if n > len(linhas) {
		n = len(linhas)
	}
	return linhas[len(linhas)-n:]
}

// ApartirDe devolve as linhas a partir da linha k (base 1), como "tail -n +k".
func ApartirDe(linhas []string, k int) []string {
	if k < 1 {
		k = 1
	}
	if k > len(linhas) {
		return linhas[len(linhas):]
	}
	return linhas[k-1:]
}

// Executar interpreta "-n N", "-nN" ou "-n +K" e escreve o trecho final da entrada.
func Executar(args []string, in io.Reader, out io.Writer) error {
	n, desdeInicio := 10, false
	for i := 0; i < len(args); i++ {
		a := args[i]
		var v string
		switch {
		case a == "-n":
			if i+1 >= len(args) {
				return fmt.Errorf("tail: -n requer um valor")
			}
			i++
			v = args[i]
		case strings.HasPrefix(a, "-n"):
			v = a[2:]
		default:
			return fmt.Errorf("tail: argumento inválido %q", a)
		}
		desdeInicio = strings.HasPrefix(v, "+")
		x, err := strconv.Atoi(strings.TrimPrefix(v, "+"))
		if err != nil || x < 0 {
			return fmt.Errorf("tail: número de linhas inválido %q", v)
		}
		n = x
	}
	dados, err := io.ReadAll(in)
	if err != nil {
		return err
	}
	if len(dados) == 0 {
		return nil
	}
	linhas := strings.Split(strings.TrimSuffix(string(dados), "\n"), "\n")
	var sel []string
	if desdeInicio {
		sel = ApartirDe(linhas, n)
	} else {
		sel = Ultimas(linhas, n)
	}
	for _, l := range sel {
		if _, err := fmt.Fprintln(out, l); err != nil {
			return err
		}
	}
	return nil
}
