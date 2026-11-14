// Pacote cut implementa uma versão simplificada do utilitário Unix cut.
package cut

import (
	"errors"
	"fmt"
	"io"
	"sort"
	"strconv"
	"strings"
)

// Faixa é um intervalo fechado de posições (base 1). Fim == 0 significa "até o final".
type Faixa struct {
	Ini, Fim int
}

// ParseLista interpreta listas como "1,3-5,7-" ou "-2".
func ParseLista(s string) ([]Faixa, error) {
	if s == "" {
		return nil, errors.New("cut: lista vazia")
	}
	var fs []Faixa
	for _, p := range strings.Split(s, ",") {
		ini, fim, tem := strings.Cut(p, "-")
		var f Faixa
		var err error
		if !tem {
			if f.Ini, err = posicao(ini); err != nil {
				return nil, err
			}
			f.Fim = f.Ini
		} else {
			f.Ini = 1
			if ini != "" {
				if f.Ini, err = posicao(ini); err != nil {
					return nil, err
				}
			}
			if fim != "" {
				if f.Fim, err = posicao(fim); err != nil {
					return nil, err
				}
				if f.Fim < f.Ini {
					return nil, fmt.Errorf("cut: faixa decrescente %q", p)
				}
			}
		}
		fs = append(fs, f)
	}
	sort.Slice(fs, func(i, j int) bool { return fs[i].Ini < fs[j].Ini })
	return fs, nil
}

func posicao(s string) (int, error) {
	n, err := strconv.Atoi(s)
	if err != nil || n < 1 {
		return 0, fmt.Errorf("cut: posição inválida %q", s)
	}
	return n, nil
}

func contem(fs []Faixa, pos int) bool {
	for _, f := range fs {
		if pos >= f.Ini && (f.Fim == 0 || pos <= f.Fim) {
			return true
		}
	}
	return false
}

// Campos seleciona os campos de uma linha separados por delim. Linhas sem o
// delimitador são devolvidas inteiras (ok=true), a menos que somenteComDelim.
func Campos(linha, delim string, fs []Faixa, somenteComDelim bool) (string, bool) {
	if !strings.Contains(linha, delim) {
		return linha, !somenteComDelim
	}
	var sel []string
	for i, c := range strings.Split(linha, delim) {
		if contem(fs, i+1) {
			sel = append(sel, c)
		}
	}
	return strings.Join(sel, delim), true
}

// Caracteres seleciona os caracteres (runas) de uma linha.
func Caracteres(linha string, fs []Faixa) string {
	var b strings.Builder
	for i, r := range []rune(linha) {
		if contem(fs, i+1) {
			b.WriteRune(r)
		}
	}
	return b.String()
}

// Executar interpreta -f LISTA [-d DELIM] [-s] ou -c LISTA.
func Executar(args []string, in io.Reader, out io.Writer) error {
	delim, lista, modo, somente := "\t", "", byte(0), false
	for i := 0; i < len(args); i++ {
		a := args[i]
		valor := func() (string, error) {
			if len(a) > 2 {
				return a[2:], nil
			}
			if i+1 >= len(args) {
				return "", fmt.Errorf("cut: %s requer um valor", a)
			}
			i++
			return args[i], nil
		}
		var err error
		switch {
		case strings.HasPrefix(a, "-d"):
			delim, err = valor()
			if err == nil && len([]rune(delim)) != 1 {
				err = errors.New("cut: o delimitador deve ser um único caractere")
			}
		case strings.HasPrefix(a, "-f"):
			modo = 'f'
			lista, err = valor()
		case strings.HasPrefix(a, "-c"):
			modo = 'c'
			lista, err = valor()
		case a == "-s":
			somente = true
		default:
			err = fmt.Errorf("cut: argumento inválido %q", a)
		}
		if err != nil {
			return err
		}
	}
	if modo == 0 {
		return errors.New("cut: informe -f ou -c")
	}
	fs, err := ParseLista(lista)
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
	for _, l := range strings.Split(strings.TrimSuffix(string(dados), "\n"), "\n") {
		if modo == 'c' {
			fmt.Fprintln(out, Caracteres(l, fs))
		} else if r, ok := Campos(l, delim, fs, somente); ok {
			fmt.Fprintln(out, r)
		}
	}
	return nil
}
