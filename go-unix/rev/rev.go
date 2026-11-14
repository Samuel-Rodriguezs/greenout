// Pacote rev implementa o utilitário Unix rev: inverte cada linha.
package rev

import (
	"bufio"
	"errors"
	"fmt"
	"io"
)

// Inverter devolve a string com as runas em ordem inversa (seguro para UTF-8).
func Inverter(s string) string {
	r := []rune(s)
	for i, j := 0, len(r)-1; i < j; i, j = i+1, j-1 {
		r[i], r[j] = r[j], r[i]
	}
	return string(r)
}

// Executar inverte cada linha da entrada. Não aceita argumentos.
func Executar(args []string, in io.Reader, out io.Writer) error {
	if len(args) > 0 {
		return fmt.Errorf("rev: argumento inesperado %q", args[0])
	}
	leitor := bufio.NewReader(in)
	for {
		linha, err := leitor.ReadString('\n')
		if len(linha) > 0 {
			terminou := linha[len(linha)-1] == '\n'
			if terminou {
				linha = linha[:len(linha)-1]
			}
			if _, e := io.WriteString(out, Inverter(linha)); e != nil {
				return e
			}
			if terminou {
				if _, e := io.WriteString(out, "\n"); e != nil {
					return e
				}
			}
		}
		if errors.Is(err, io.EOF) {
			return nil
		}
		if err != nil {
			return err
		}
	}
}
