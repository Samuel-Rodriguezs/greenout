// Pacote basename implementa o utilitário Unix basename.
package basename

import (
	"errors"
	"fmt"
	"io"
	"strings"
)

// Base devolve o último componente do caminho, removendo barras finais e,
// opcionalmente, um sufixo (que nunca elimina o nome inteiro).
func Base(caminho, sufixo string) string {
	if caminho == "" {
		return ""
	}
	t := strings.TrimRight(caminho, "/")
	if t == "" {
		return "/"
	}
	if i := strings.LastIndexByte(t, '/'); i >= 0 {
		t = t[i+1:]
	}
	if sufixo != "" && t != sufixo && strings.HasSuffix(t, sufixo) {
		t = strings.TrimSuffix(t, sufixo)
	}
	return t
}

// Executar interpreta NOME [SUFIXO].
func Executar(args []string, in io.Reader, out io.Writer) error {
	if len(args) == 0 {
		return errors.New("basename: operando ausente")
	}
	if len(args) > 2 {
		return fmt.Errorf("basename: operando extra %q", args[2])
	}
	sufixo := ""
	if len(args) == 2 {
		sufixo = args[1]
	}
	_, err := fmt.Fprintln(out, Base(args[0], sufixo))
	return err
}
