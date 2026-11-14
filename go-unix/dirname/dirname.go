// Pacote dirname implementa o utilitário Unix dirname.
package dirname

import (
	"errors"
	"fmt"
	"io"
	"strings"
)

// Dir devolve o caminho sem o último componente, seguindo a semântica do
// dirname POSIX: "" e nomes sem barra viram ".", e a raiz permanece "/".
func Dir(caminho string) string {
	if caminho == "" {
		return "."
	}
	t := strings.TrimRight(caminho, "/")
	if t == "" {
		return "/"
	}
	i := strings.LastIndexByte(t, '/')
	if i < 0 {
		return "."
	}
	d := strings.TrimRight(t[:i], "/")
	if d == "" {
		return "/"
	}
	return d
}

// Executar interpreta NOME... e imprime o diretório de cada um.
func Executar(args []string, in io.Reader, out io.Writer) error {
	if len(args) == 0 {
		return errors.New("dirname: operando ausente")
	}
	for _, a := range args {
		if _, err := fmt.Fprintln(out, Dir(a)); err != nil {
			return err
		}
	}
	return nil
}
