// Pacote comm implementa uma versão simplificada do utilitário Unix comm.
package comm

import (
	"errors"
	"fmt"
	"io"
	"os"
	"strings"
)

// Linha é uma linha da comparação e a coluna onde aparece:
// 1 = só no primeiro, 2 = só no segundo, 3 = em ambos.
type Linha struct {
	Coluna int
	Texto  string
}

// Comparar faz o merge de duas listas já ordenadas lexicograficamente.
func Comparar(a, b []string) []Linha {
	var res []Linha
	i, j := 0, 0
	for i < len(a) || j < len(b) {
		switch {
		case j >= len(b) || (i < len(a) && a[i] < b[j]):
			res = append(res, Linha{1, a[i]})
			i++
		case i >= len(a) || b[j] < a[i]:
			res = append(res, Linha{2, b[j]})
			j++
		default:
			res = append(res, Linha{3, a[i]})
			i++
			j++
		}
	}
	return res
}

// Formatar monta a saída, suprimindo as colunas indicadas e usando tabs de
// recuo conforme as colunas anteriores visíveis.
func Formatar(ls []Linha, suprimir [4]bool) []string {
	var res []string
	for _, l := range ls {
		if suprimir[l.Coluna] {
			continue
		}
		recuo := 0
		for c := 1; c < l.Coluna; c++ {
			if !suprimir[c] {
				recuo++
			}
		}
		res = append(res, strings.Repeat("\t", recuo)+l.Texto)
	}
	return res
}

func lerLinhas(nome string, in io.Reader) ([]string, error) {
	var dados []byte
	var err error
	if nome == "-" {
		dados, err = io.ReadAll(in)
	} else {
		dados, err = os.ReadFile(nome)
	}
	if err != nil {
		return nil, fmt.Errorf("comm: %w", err)
	}
	if len(dados) == 0 {
		return nil, nil
	}
	return strings.Split(strings.TrimSuffix(string(dados), "\n"), "\n"), nil
}

// Executar interpreta [-1] [-2] [-3] ARQ1 ARQ2; "-" lê a entrada padrão.
func Executar(args []string, in io.Reader, out io.Writer) error {
	var suprimir [4]bool
	var arquivos []string
	for _, a := range args {
		if len(a) > 1 && a[0] == '-' && strings.Trim(a[1:], "123") == "" {
			for _, c := range a[1:] {
				suprimir[c-'0'] = true
			}
			continue
		}
		arquivos = append(arquivos, a)
	}
	if len(arquivos) != 2 {
		return errors.New("comm: uso: comm [-123] ARQ1 ARQ2")
	}
	if arquivos[0] == "-" && arquivos[1] == "-" {
		return errors.New("comm: apenas um operando pode ser a entrada padrão")
	}
	a, err := lerLinhas(arquivos[0], in)
	if err != nil {
		return err
	}
	b, err := lerLinhas(arquivos[1], in)
	if err != nil {
		return err
	}
	for _, l := range Formatar(Comparar(a, b), suprimir) {
		if _, err := fmt.Fprintln(out, l); err != nil {
			return err
		}
	}
	return nil
}
