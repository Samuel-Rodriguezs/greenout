// Pacote argumentos implementa um parser de argumentos de linha de comando
// no estilo flag: --nome=valor, --nome valor, -n valor e flags booleanas.
package argumentos

import (
	"errors"
	"fmt"
	"strconv"
	"strings"
)

// Erros possíveis.
var (
	ErrDesconhecida = errors.New("argumentos: flag desconhecida")
	ErrSemValor     = errors.New("argumentos: flag sem valor")
	ErrValor        = errors.New("argumentos: valor inválido")
)

type definicao struct {
	nome, curto string
	bool_       bool
	ptrStr      *string
	ptrInt      *int
	ptrBool     *bool
}

// Parser guarda as flags registradas.
type Parser struct {
	defs []*definicao
}

// Texto registra uma flag de texto.
func (p *Parser) Texto(nome, curto string, padrao string) *string {
	v := padrao
	p.defs = append(p.defs, &definicao{nome: nome, curto: curto, ptrStr: &v})
	return &v
}

// Inteiro registra uma flag numérica.
func (p *Parser) Inteiro(nome, curto string, padrao int) *int {
	v := padrao
	p.defs = append(p.defs, &definicao{nome: nome, curto: curto, ptrInt: &v})
	return &v
}

// Booleano registra uma flag que não exige valor.
func (p *Parser) Booleano(nome, curto string) *bool {
	v := false
	p.defs = append(p.defs, &definicao{nome: nome, curto: curto, bool_: true, ptrBool: &v})
	return &v
}

func (p *Parser) buscar(chave string) *definicao {
	for _, d := range p.defs {
		if chave == "--"+d.nome || (d.curto != "" && chave == "-"+d.curto) {
			return d
		}
	}
	return nil
}

// Interpretar processa os argumentos e devolve os posicionais.
// O marcador "--" encerra as flags.
func (p *Parser) Interpretar(args []string) ([]string, error) {
	var posicionais []string
	for i := 0; i < len(args); i++ {
		a := args[i]
		if a == "--" {
			return append(posicionais, args[i+1:]...), nil
		}
		if !strings.HasPrefix(a, "-") || a == "-" {
			posicionais = append(posicionais, a)
			continue
		}
		chave, valor, temValor := strings.Cut(a, "=")
		d := p.buscar(chave)
		if d == nil {
			return nil, fmt.Errorf("%w: %s", ErrDesconhecida, chave)
		}
		if d.bool_ {
			*d.ptrBool = true
			if temValor {
				b, err := strconv.ParseBool(valor)
				if err != nil {
					return nil, fmt.Errorf("%w: %s=%s", ErrValor, chave, valor)
				}
				*d.ptrBool = b
			}
			continue
		}
		if !temValor {
			if i+1 >= len(args) {
				return nil, fmt.Errorf("%w: %s", ErrSemValor, chave)
			}
			i++
			valor = args[i]
		}
		if d.ptrInt != nil {
			n, err := strconv.Atoi(valor)
			if err != nil {
				return nil, fmt.Errorf("%w: %s=%s", ErrValor, chave, valor)
			}
			*d.ptrInt = n
		} else {
			*d.ptrStr = valor
		}
	}
	return posicionais, nil
}
