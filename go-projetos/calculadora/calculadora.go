// Pacote calculadora avalia expressões aritméticas com tokenizador e
// parser de descida recursiva (+ - * / ^, parênteses, menos unário).
package calculadora

import (
	"errors"
	"fmt"
	"math"
	"strconv"
	"unicode"
)

// Erros possíveis.
var (
	ErrDivisaoPorZero = errors.New("calculadora: divisão por zero")
	ErrSintaxe        = errors.New("calculadora: erro de sintaxe")
)

type tipoToken int

const (
	tNum tipoToken = iota
	tOp
	tAbre
	tFecha
	tFim
)

type token struct {
	tipo  tipoToken
	texto string
	num   float64
}

// tokenizar converte o texto em uma lista de tokens.
func tokenizar(s string) ([]token, error) {
	var ts []token
	r := []rune(s)
	for i := 0; i < len(r); {
		c := r[i]
		switch {
		case unicode.IsSpace(c):
			i++
		case unicode.IsDigit(c) || c == '.':
			j := i
			for j < len(r) && (unicode.IsDigit(r[j]) || r[j] == '.') {
				j++
			}
			v, err := strconv.ParseFloat(string(r[i:j]), 64)
			if err != nil {
				return nil, fmt.Errorf("%w: número %q", ErrSintaxe, string(r[i:j]))
			}
			ts = append(ts, token{tipo: tNum, num: v})
			i = j
		case c == '+' || c == '-' || c == '*' || c == '/' || c == '^':
			ts = append(ts, token{tipo: tOp, texto: string(c)})
			i++
		case c == '(':
			ts = append(ts, token{tipo: tAbre})
			i++
		case c == ')':
			ts = append(ts, token{tipo: tFecha})
			i++
		default:
			return nil, fmt.Errorf("%w: caractere %q", ErrSintaxe, c)
		}
	}
	return append(ts, token{tipo: tFim}), nil
}

type parser struct {
	ts  []token
	pos int
}

func (p *parser) atual() token { return p.ts[p.pos] }

// expr = termo (('+'|'-') termo)*
func (p *parser) expr() (float64, error) {
	v, err := p.termo()
	for err == nil && p.atual().tipo == tOp && (p.atual().texto == "+" || p.atual().texto == "-") {
		op := p.atual().texto
		p.pos++
		var d float64
		if d, err = p.termo(); err != nil {
			break
		}
		if op == "+" {
			v += d
		} else {
			v -= d
		}
	}
	return v, err
}

// termo = potencia (('*'|'/') potencia)*
func (p *parser) termo() (float64, error) {
	v, err := p.potencia()
	for err == nil && p.atual().tipo == tOp && (p.atual().texto == "*" || p.atual().texto == "/") {
		op := p.atual().texto
		p.pos++
		var d float64
		if d, err = p.potencia(); err != nil {
			break
		}
		if op == "*" {
			v *= d
		} else if d == 0 {
			return 0, ErrDivisaoPorZero
		} else {
			v /= d
		}
	}
	return v, err
}

// potencia = unario ('^' potencia)?  (associativa à direita)
func (p *parser) potencia() (float64, error) {
	base, err := p.unario()
	if err != nil {
		return 0, err
	}
	if p.atual().tipo == tOp && p.atual().texto == "^" {
		p.pos++
		exp, err := p.potencia()
		if err != nil {
			return 0, err
		}
		return math.Pow(base, exp), nil
	}
	return base, nil
}

// unario = '-' unario | primario
func (p *parser) unario() (float64, error) {
	if p.atual().tipo == tOp && p.atual().texto == "-" {
		p.pos++
		v, err := p.unario()
		return -v, err
	}
	return p.primario()
}

func (p *parser) primario() (float64, error) {
	t := p.atual()
	switch t.tipo {
	case tNum:
		p.pos++
		return t.num, nil
	case tAbre:
		p.pos++
		v, err := p.expr()
		if err != nil {
			return 0, err
		}
		if p.atual().tipo != tFecha {
			return 0, fmt.Errorf("%w: parêntese não fechado", ErrSintaxe)
		}
		p.pos++
		return v, nil
	}
	return 0, fmt.Errorf("%w: token inesperado", ErrSintaxe)
}

// Avaliar calcula o valor da expressão.
func Avaliar(s string) (float64, error) {
	ts, err := tokenizar(s)
	if err != nil {
		return 0, err
	}
	p := &parser{ts: ts}
	v, err := p.expr()
	if err != nil {
		return 0, err
	}
	if p.atual().tipo != tFim {
		return 0, fmt.Errorf("%w: sobrou entrada", ErrSintaxe)
	}
	return v, nil
}
