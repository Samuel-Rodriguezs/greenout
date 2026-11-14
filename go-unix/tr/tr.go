// Pacote tr implementa uma versão simplificada do utilitário Unix tr.
package tr

import (
	"errors"
	"fmt"
	"io"
	"strings"
)

// Expandir converte uma especificação de conjunto em runas, tratando faixas
// (a-z), escapes (\n \t \\ \-) e as classes [:lower:] [:upper:] [:digit:] [:space:].
func Expandir(spec string) ([]rune, error) {
	classes := map[string]string{
		"[:lower:]": "abcdefghijklmnopqrstuvwxyz",
		"[:upper:]": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
		"[:digit:]": "0123456789",
		"[:space:]": " \t\n\r\v\f",
	}
	var res []rune
	rs := []rune(spec)
	for i := 0; i < len(rs); i++ {
		if rs[i] == '[' {
			achou := false
			for nome, conj := range classes {
				if strings.HasPrefix(string(rs[i:]), nome) {
					res = append(res, []rune(conj)...)
					i += len([]rune(nome)) - 1
					achou = true
					break
				}
			}
			if achou {
				continue
			}
		}
		c := rs[i]
		if c == '\\' {
			if i+1 >= len(rs) {
				return nil, errors.New("tr: escape incompleto")
			}
			i++
			switch rs[i] {
			case 'n':
				c = '\n'
			case 't':
				c = '\t'
			case 'r':
				c = '\r'
			default:
				c = rs[i]
			}
			res = append(res, c)
			continue
		}
		if i+2 < len(rs) && rs[i+1] == '-' {
			fim := rs[i+2]
			if fim < c {
				return nil, fmt.Errorf("tr: faixa inválida %c-%c", c, fim)
			}
			for x := c; x <= fim; x++ {
				res = append(res, x)
			}
			i += 2
			continue
		}
		res = append(res, c)
	}
	return res, nil
}

// Opcoes define a operação do tr.
type Opcoes struct {
	Deletar   bool // -d
	Comprimir bool // -s
	Conj1     []rune
	Conj2     []rune
}

// Traduzir aplica a operação ao texto.
func Traduzir(s string, o Opcoes) string {
	mapa := map[rune]rune{}
	if !o.Deletar && len(o.Conj2) > 0 {
		for i, r := range o.Conj1 {
			j := i
			if j >= len(o.Conj2) {
				j = len(o.Conj2) - 1
			}
			if _, existe := mapa[r]; !existe {
				mapa[r] = o.Conj2[j]
			}
		}
	}
	del := map[rune]bool{}
	if o.Deletar {
		for _, r := range o.Conj1 {
			del[r] = true
		}
	}
	// conjunto usado para comprimir repetições
	comp := map[rune]bool{}
	if o.Comprimir {
		base := o.Conj1
		if len(o.Conj2) > 0 {
			base = o.Conj2
		}
		for _, r := range base {
			comp[r] = true
		}
	}
	var b strings.Builder
	var ultimo rune
	tem := false
	for _, r := range s {
		if del[r] {
			continue
		}
		if m, ok := mapa[r]; ok {
			r = m
		}
		if o.Comprimir && comp[r] && tem && ultimo == r {
			continue
		}
		b.WriteRune(r)
		ultimo, tem = r, true
	}
	return b.String()
}

// Executar interpreta [-d] [-s] CONJ1 [CONJ2].
func Executar(args []string, in io.Reader, out io.Writer) error {
	var o Opcoes
	var conjs []string
	for _, a := range args {
		switch {
		case a == "-d":
			o.Deletar = true
		case a == "-s":
			o.Comprimir = true
		case a == "-ds" || a == "-sd":
			o.Deletar, o.Comprimir = true, true
		default:
			conjs = append(conjs, a)
		}
	}
	if len(conjs) == 0 {
		return errors.New("tr: operando ausente")
	}
	if len(conjs) > 2 {
		return errors.New("tr: operandos demais")
	}
	var err error
	if o.Conj1, err = Expandir(conjs[0]); err != nil {
		return err
	}
	if len(conjs) == 2 {
		if o.Deletar && !o.Comprimir {
			return errors.New("tr: -d aceita apenas um conjunto")
		}
		if o.Conj2, err = Expandir(conjs[1]); err != nil {
			return err
		}
	}
	if !o.Deletar && !o.Comprimir && len(conjs) < 2 {
		return errors.New("tr: falta o segundo conjunto")
	}
	dados, err := io.ReadAll(in)
	if err != nil {
		return err
	}
	_, err = io.WriteString(out, Traduzir(string(dados), o))
	return err
}
