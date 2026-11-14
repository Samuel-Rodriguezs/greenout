// Pacote uniq implementa uma versão simplificada do utilitário Unix uniq.
package uniq

import (
	"fmt"
	"io"
	"strings"
)

// Grupo é uma sequência de linhas adjacentes consideradas iguais.
type Grupo struct {
	Linha string // primeira linha do grupo
	N     int    // quantidade de ocorrências
}

// Agrupar junta linhas adjacentes iguais (opcionalmente ignorando a caixa).
func Agrupar(linhas []string, ignorarCaixa bool) []Grupo {
	var gs []Grupo
	igual := func(a, b string) bool {
		if ignorarCaixa {
			return strings.EqualFold(a, b)
		}
		return a == b
	}
	for _, l := range linhas {
		if n := len(gs); n > 0 && igual(gs[n-1].Linha, l) {
			gs[n-1].N++
			continue
		}
		gs = append(gs, Grupo{Linha: l, N: 1})
	}
	return gs
}

// Executar interpreta [-c] [-d] [-u] [-i]: contar, só repetidas, só únicas, ignorar caixa.
func Executar(args []string, in io.Reader, out io.Writer) error {
	var contar, repetidas, unicas, ignorar bool
	for _, a := range args {
		if len(a) < 2 || a[0] != '-' {
			return fmt.Errorf("uniq: argumento inválido %q", a)
		}
		for _, f := range a[1:] {
			switch f {
			case 'c':
				contar = true
			case 'd':
				repetidas = true
			case 'u':
				unicas = true
			case 'i':
				ignorar = true
			default:
				return fmt.Errorf("uniq: opção inválida -%c", f)
			}
		}
	}
	if repetidas && unicas {
		return fmt.Errorf("uniq: -d e -u são incompatíveis")
	}
	dados, err := io.ReadAll(in)
	if err != nil {
		return err
	}
	if len(dados) == 0 {
		return nil
	}
	linhas := strings.Split(strings.TrimSuffix(string(dados), "\n"), "\n")
	for _, g := range Agrupar(linhas, ignorar) {
		if repetidas && g.N < 2 || unicas && g.N > 1 {
			continue
		}
		if contar {
			fmt.Fprintf(out, "%7d %s\n", g.N, g.Linha)
		} else {
			fmt.Fprintln(out, g.Linha)
		}
	}
	return nil
}
