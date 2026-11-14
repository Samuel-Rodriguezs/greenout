// Pacote seq implementa uma versão simplificada do utilitário Unix seq.
package seq

import (
	"errors"
	"fmt"
	"io"
	"math"
	"strconv"
	"strings"
)

// limiteItens evita geração acidental de sequências gigantes.
const limiteItens = 10_000_000

// casasDecimais conta as casas decimais usadas na representação textual de um número.
func casasDecimais(s string) int {
	if i := strings.IndexByte(s, '.'); i >= 0 {
		return len(s) - i - 1
	}
	return 0
}

// Sequencia gera os valores de ini até fim (inclusive) com o passo dado,
// formatados com a quantidade de casas indicada. Passo zero é erro; se o passo
// aponta para longe do fim, a sequência é vazia.
func Sequencia(ini, passo, fim float64, casas int) ([]string, error) {
	if passo == 0 {
		return nil, errors.New("seq: o incremento não pode ser zero")
	}
	n := math.Floor((fim-ini)/passo+1e-9) + 1
	if n <= 0 {
		return []string{}, nil
	}
	if n > limiteItens {
		return nil, errors.New("seq: sequência grande demais")
	}
	res := make([]string, 0, int(n))
	for i := 0; i < int(n); i++ {
		res = append(res, strconv.FormatFloat(ini+float64(i)*passo, 'f', casas, 64))
	}
	return res, nil
}

// Executar interpreta [-s SEP] [-w] [INICIO [PASSO]] FIM.
func Executar(args []string, in io.Reader, out io.Writer) error {
	sep, igualar := "\n", false
	var nums []string
	for i := 0; i < len(args); i++ {
		a := args[i]
		switch {
		case a == "-w":
			igualar = true
		case a == "-s":
			if i+1 >= len(args) {
				return errors.New("seq: -s requer um valor")
			}
			i++
			sep = args[i]
		default:
			nums = append(nums, a)
		}
	}
	if len(nums) == 0 || len(nums) > 3 {
		return errors.New("seq: uso: seq [-s SEP] [-w] [INICIO [PASSO]] FIM")
	}
	vals := make([]float64, len(nums))
	casas := 0
	for i, s := range nums {
		v, err := strconv.ParseFloat(s, 64)
		if err != nil || math.IsNaN(v) || math.IsInf(v, 0) {
			return fmt.Errorf("seq: número inválido %q", s)
		}
		vals[i] = v
		if c := casasDecimais(s); c > casas {
			casas = c
		}
	}
	ini, passo, fim := 1.0, 1.0, vals[len(vals)-1]
	switch len(vals) {
	case 2:
		ini = vals[0]
	case 3:
		ini, passo = vals[0], vals[1]
	}
	itens, err := Sequencia(ini, passo, fim, casas)
	if err != nil {
		return err
	}
	if igualar {
		largura := 0
		for _, s := range itens {
			if len(s) > largura {
				largura = len(s)
			}
		}
		for i, s := range itens {
			neg := strings.HasPrefix(s, "-")
			corpo := strings.TrimPrefix(s, "-")
			zeros := largura - len(s)
			if zeros > 0 {
				corpo = strings.Repeat("0", zeros) + corpo
			}
			if neg {
				corpo = "-" + corpo
			}
			itens[i] = corpo
		}
	}
	if len(itens) == 0 {
		return nil
	}
	_, err = io.WriteString(out, strings.Join(itens, sep)+"\n")
	return err
}
