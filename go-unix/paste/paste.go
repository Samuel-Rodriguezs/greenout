// Pacote paste implementa uma versão simplificada do utilitário Unix paste.
package paste

import (
	"errors"
	"fmt"
	"io"
	"os"
	"strings"
)

// Colar junta linha a linha as colunas (uma por arquivo), separadas pelos
// delimitadores, que são usados ciclicamente. Colunas mais curtas contribuem
// com texto vazio.
func Colar(colunas [][]string, delims []rune) []string {
	if len(delims) == 0 {
		delims = []rune{'\t'}
	}
	max := 0
	for _, c := range colunas {
		if len(c) > max {
			max = len(c)
		}
	}
	res := make([]string, 0, max)
	for i := 0; i < max; i++ {
		var b strings.Builder
		for j, c := range colunas {
			if j > 0 {
				b.WriteRune(delims[(j-1)%len(delims)])
			}
			if i < len(c) {
				b.WriteString(c[i])
			}
		}
		res = append(res, b.String())
	}
	return res
}

// Serial junta todas as linhas de cada coluna em uma única linha (modo -s).
func Serial(colunas [][]string, delims []rune) []string {
	if len(delims) == 0 {
		delims = []rune{'\t'}
	}
	res := make([]string, 0, len(colunas))
	for _, c := range colunas {
		var b strings.Builder
		for i, l := range c {
			if i > 0 {
				b.WriteRune(delims[(i-1)%len(delims)])
			}
			b.WriteString(l)
		}
		res = append(res, b.String())
	}
	return res
}

func linhasDe(dados []byte) []string {
	if len(dados) == 0 {
		return nil
	}
	return strings.Split(strings.TrimSuffix(string(dados), "\n"), "\n")
}

// Executar interpreta [-s] [-d DELIMS] [ARQUIVO...]; "-" lê a entrada padrão.
func Executar(args []string, in io.Reader, out io.Writer) error {
	delims := []rune{'\t'}
	serial := false
	var arquivos []string
	for i := 0; i < len(args); i++ {
		a := args[i]
		switch {
		case a == "-s":
			serial = true
		case a == "-d":
			if i+1 >= len(args) {
				return errors.New("paste: -d requer um valor")
			}
			i++
			delims = []rune(args[i])
		case strings.HasPrefix(a, "-d"):
			delims = []rune(a[2:])
		case a == "-" || a == "" || a[0] != '-':
			arquivos = append(arquivos, a)
		default:
			return fmt.Errorf("paste: opção inválida %q", a)
		}
	}
	if len(delims) == 0 {
		return errors.New("paste: delimitador vazio")
	}
	if len(arquivos) == 0 {
		arquivos = []string{"-"}
	}
	var colunas [][]string
	for _, nome := range arquivos {
		var dados []byte
		var err error
		if nome == "-" {
			dados, err = io.ReadAll(in)
		} else {
			dados, err = os.ReadFile(nome)
		}
		if err != nil {
			return fmt.Errorf("paste: %w", err)
		}
		colunas = append(colunas, linhasDe(dados))
	}
	var linhas []string
	if serial {
		linhas = Serial(colunas, delims)
	} else {
		linhas = Colar(colunas, delims)
	}
	for _, l := range linhas {
		if _, err := fmt.Fprintln(out, l); err != nil {
			return err
		}
	}
	return nil
}
