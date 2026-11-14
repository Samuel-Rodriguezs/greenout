// Pacote cat implementa uma versão simplificada do utilitário Unix cat.
package cat

import (
	"fmt"
	"io"
	"os"
	"strings"
)

// Opcoes controla a formatação da saída.
type Opcoes struct {
	Numerar   bool // -n: numera todas as linhas
	Comprimir bool // -s: junta linhas em branco consecutivas
	FimLinha  bool // -E: marca o fim de cada linha com $
}

// Formatar aplica as opções ao texto. O contador de linhas começa em 1.
func Formatar(texto string, o Opcoes) string {
	if texto == "" {
		return ""
	}
	terminaComNL := strings.HasSuffix(texto, "\n")
	linhas := strings.Split(strings.TrimSuffix(texto, "\n"), "\n")
	var b strings.Builder
	num, anteriorVazia := 0, false
	for i, l := range linhas {
		vazia := l == ""
		if o.Comprimir && vazia && anteriorVazia {
			continue
		}
		anteriorVazia = vazia
		num++
		if o.Numerar {
			fmt.Fprintf(&b, "%6d\t", num)
		}
		b.WriteString(l)
		if o.FimLinha {
			b.WriteByte('$')
		}
		if i < len(linhas)-1 || terminaComNL {
			b.WriteByte('\n')
		}
	}
	return b.String()
}

// Executar interpreta [-n] [-s] [-E] [ARQUIVO...]; "-" ou ausência de
// arquivos significa entrada padrão.
func Executar(args []string, in io.Reader, out io.Writer) error {
	var o Opcoes
	var arquivos []string
	for _, a := range args {
		if len(a) > 1 && a[0] == '-' {
			for _, f := range a[1:] {
				switch f {
				case 'n':
					o.Numerar = true
				case 's':
					o.Comprimir = true
				case 'E':
					o.FimLinha = true
				default:
					return fmt.Errorf("cat: opção inválida -%c", f)
				}
			}
			continue
		}
		arquivos = append(arquivos, a)
	}
	if len(arquivos) == 0 {
		arquivos = []string{"-"}
	}
	var todo strings.Builder
	for _, nome := range arquivos {
		var dados []byte
		var err error
		if nome == "-" {
			dados, err = io.ReadAll(in)
		} else {
			dados, err = os.ReadFile(nome)
		}
		if err != nil {
			return fmt.Errorf("cat: %w", err)
		}
		todo.Write(dados)
	}
	_, err := io.WriteString(out, Formatar(todo.String(), o))
	return err
}
