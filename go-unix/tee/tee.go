// Pacote tee implementa uma versão simplificada do utilitário Unix tee.
package tee

import (
	"errors"
	"fmt"
	"io"
	"os"
)

// Duplicar copia a entrada para a saída principal e para todos os destinos extras.
// Devolve o número de bytes copiados.
func Duplicar(in io.Reader, out io.Writer, extras ...io.Writer) (int64, error) {
	destinos := append([]io.Writer{out}, extras...)
	return io.Copy(io.MultiWriter(destinos...), in)
}

// Executar interpreta [-a] [ARQUIVO...]. Com -a os arquivos são anexados em vez de truncados.
func Executar(args []string, in io.Reader, out io.Writer) error {
	anexar := false
	var nomes []string
	for _, a := range args {
		if a == "-a" {
			anexar = true
			continue
		}
		if len(a) > 1 && a[0] == '-' {
			return fmt.Errorf("tee: opção inválida %q", a)
		}
		nomes = append(nomes, a)
	}
	flags := os.O_WRONLY | os.O_CREATE | os.O_TRUNC
	if anexar {
		flags = os.O_WRONLY | os.O_CREATE | os.O_APPEND
	}
	var arquivos []*os.File
	var extras []io.Writer
	var erros []error
	for _, n := range nomes {
		f, err := os.OpenFile(n, flags, 0o644)
		if err != nil {
			erros = append(erros, fmt.Errorf("tee: %w", err))
			continue
		}
		arquivos = append(arquivos, f)
		extras = append(extras, f)
	}
	_, err := Duplicar(in, out, extras...)
	if err != nil {
		erros = append(erros, err)
	}
	for _, f := range arquivos {
		if err := f.Close(); err != nil {
			erros = append(erros, err)
		}
	}
	return errors.Join(erros...)
}
