// Pacote wc implementa uma versão simplificada do utilitário Unix wc.
package wc

import (
	"fmt"
	"io"
	"strings"
	"unicode/utf8"
)

// Contagem reúne os totais calculados sobre uma entrada.
type Contagem struct {
	Linhas, Palavras, Bytes, Caracteres int
}

// Contar lê toda a entrada e devolve as contagens.
func Contar(r io.Reader) (Contagem, error) {
	dados, err := io.ReadAll(r)
	if err != nil {
		return Contagem{}, err
	}
	s := string(dados)
	return Contagem{
		Linhas:     strings.Count(s, "\n"),
		Palavras:   len(strings.Fields(s)),
		Bytes:      len(dados),
		Caracteres: utf8.RuneCountInString(s),
	}, nil
}

// Executar processa os argumentos (-l -w -c -m, combináveis) e escreve o resultado.
// Sem opções, imprime linhas, palavras e bytes.
func Executar(args []string, in io.Reader, out io.Writer) error {
	var l, w, c, m bool
	for _, a := range args {
		if len(a) < 2 || a[0] != '-' {
			return fmt.Errorf("wc: argumento inválido %q", a)
		}
		for _, f := range a[1:] {
			switch f {
			case 'l':
				l = true
			case 'w':
				w = true
			case 'c':
				c = true
			case 'm':
				m = true
			default:
				return fmt.Errorf("wc: opção inválida -%c", f)
			}
		}
	}
	if !l && !w && !c && !m {
		l, w, c = true, true, true
	}
	ct, err := Contar(in)
	if err != nil {
		return err
	}
	var campos []string
	if l {
		campos = append(campos, fmt.Sprint(ct.Linhas))
	}
	if w {
		campos = append(campos, fmt.Sprint(ct.Palavras))
	}
	if m {
		campos = append(campos, fmt.Sprint(ct.Caracteres))
	}
	if c {
		campos = append(campos, fmt.Sprint(ct.Bytes))
	}
	_, err = fmt.Fprintln(out, strings.Join(campos, " "))
	return err
}
