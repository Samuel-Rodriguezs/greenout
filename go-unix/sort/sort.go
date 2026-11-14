// Pacote sort implementa uma versão simplificada do utilitário Unix sort.
package sort

import (
	"fmt"
	"io"
	"sort"
	"strconv"
	"strings"
)

// Opcoes controla a ordenação.
type Opcoes struct {
	Reverso      bool // -r
	Numerico     bool // -n
	Unico        bool // -u
	IgnorarCaixa bool // -f
}

// valorNumerico extrai o número no início da linha (0 se não houver).
func valorNumerico(s string) float64 {
	s = strings.TrimLeft(s, " \t")
	fim := 0
	for fim < len(s) && strings.IndexByte("+-0123456789.", s[fim]) >= 0 {
		fim++
	}
	for ; fim > 0; fim-- {
		if v, err := strconv.ParseFloat(s[:fim], 64); err == nil {
			return v
		}
	}
	return 0
}

// Ordenar devolve uma cópia ordenada das linhas.
func Ordenar(linhas []string, o Opcoes) []string {
	r := append([]string(nil), linhas...)
	chave := func(s string) string {
		if o.IgnorarCaixa {
			return strings.ToLower(s)
		}
		return s
	}
	menor := func(a, b string) bool {
		if o.Numerico {
			va, vb := valorNumerico(a), valorNumerico(b)
			if va != vb {
				return va < vb
			}
		}
		return chave(a) < chave(b)
	}
	sort.SliceStable(r, func(i, j int) bool {
		if o.Reverso {
			return menor(r[j], r[i])
		}
		return menor(r[i], r[j])
	})
	if o.Unico {
		var u []string
		for _, l := range r {
			if len(u) == 0 || menor(u[len(u)-1], l) || menor(l, u[len(u)-1]) {
				u = append(u, l)
			}
		}
		r = u
	}
	return r
}

// Executar interpreta [-rnuf] e ordena as linhas da entrada.
func Executar(args []string, in io.Reader, out io.Writer) error {
	var o Opcoes
	for _, a := range args {
		if len(a) < 2 || a[0] != '-' {
			return fmt.Errorf("sort: argumento inválido %q", a)
		}
		for _, f := range a[1:] {
			switch f {
			case 'r':
				o.Reverso = true
			case 'n':
				o.Numerico = true
			case 'u':
				o.Unico = true
			case 'f':
				o.IgnorarCaixa = true
			default:
				return fmt.Errorf("sort: opção inválida -%c", f)
			}
		}
	}
	dados, err := io.ReadAll(in)
	if err != nil {
		return err
	}
	if len(dados) == 0 {
		return nil
	}
	linhas := strings.Split(strings.TrimSuffix(string(dados), "\n"), "\n")
	for _, l := range Ordenar(linhas, o) {
		if _, err := fmt.Fprintln(out, l); err != nil {
			return err
		}
	}
	return nil
}
