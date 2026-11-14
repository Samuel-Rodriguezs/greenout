// Pacote flags é um parser de linha de comando próprio, sem depender do pacote flag.
//
// Formas aceitas: --nome=valor, --nome valor, -n valor, -n=valor, --bool,
// --bool=false, "--" (encerra as opções) e argumentos posicionais intercalados.
package flags

import (
	"fmt"
	"sort"
	"strconv"
	"strings"
	"time"
)

type definicao struct {
	nome    string
	curto   byte
	uso     string
	ehBool  bool
	definir func(string) error
	padrao  string
}

// Conjunto reúne as flags de um programa.
type Conjunto struct {
	nome   string
	defs   map[string]*definicao
	curtos map[byte]*definicao
	pos    []string
}

// Novo cria um conjunto de flags para o programa "nome".
func Novo(nome string) *Conjunto {
	return &Conjunto{nome: nome, defs: map[string]*definicao{}, curtos: map[byte]*definicao{}}
}

func (c *Conjunto) registrar(d *definicao) {
	if _, dup := c.defs[d.nome]; dup {
		panic("flags: flag duplicada --" + d.nome)
	}
	c.defs[d.nome] = d
	if d.curto != 0 {
		if _, dup := c.curtos[d.curto]; dup {
			panic("flags: atalho duplicado -" + string(d.curto))
		}
		c.curtos[d.curto] = d
	}
}

// Texto registra uma flag de texto. curto = 0 significa sem atalho.
func (c *Conjunto) Texto(nome string, curto byte, padrao, uso string) *string {
	p := new(string)
	*p = padrao
	c.registrar(&definicao{nome: nome, curto: curto, uso: uso, padrao: padrao,
		definir: func(s string) error { *p = s; return nil }})
	return p
}

// Inteiro registra uma flag inteira.
func (c *Conjunto) Inteiro(nome string, curto byte, padrao int, uso string) *int {
	p := new(int)
	*p = padrao
	c.registrar(&definicao{nome: nome, curto: curto, uso: uso, padrao: strconv.Itoa(padrao),
		definir: func(s string) error {
			n, err := strconv.Atoi(s)
			if err != nil {
				return fmt.Errorf("valor inteiro inválido %q", s)
			}
			*p = n
			return nil
		}})
	return p
}

// Bool registra uma flag booleana (não consome o próximo argumento).
func (c *Conjunto) Bool(nome string, curto byte, padrao bool, uso string) *bool {
	p := new(bool)
	*p = padrao
	c.registrar(&definicao{nome: nome, curto: curto, uso: uso, ehBool: true, padrao: strconv.FormatBool(padrao),
		definir: func(s string) error {
			b, err := strconv.ParseBool(s)
			if err != nil {
				return fmt.Errorf("valor booleano inválido %q", s)
			}
			*p = b
			return nil
		}})
	return p
}

// Duracao registra uma flag de duração (ex.: "1m30s").
func (c *Conjunto) Duracao(nome string, curto byte, padrao time.Duration, uso string) *time.Duration {
	p := new(time.Duration)
	*p = padrao
	c.registrar(&definicao{nome: nome, curto: curto, uso: uso, padrao: padrao.String(),
		definir: func(s string) error {
			d, err := time.ParseDuration(s)
			if err != nil {
				return fmt.Errorf("duração inválida %q", s)
			}
			*p = d
			return nil
		}})
	return p
}

// Parse interpreta args (sem o nome do programa).
func (c *Conjunto) Parse(args []string) error {
	c.pos = nil
	for i := 0; i < len(args); i++ {
		a := args[i]
		switch {
		case a == "--":
			c.pos = append(c.pos, args[i+1:]...)
			return nil
		case a == "-" || !strings.HasPrefix(a, "-"):
			c.pos = append(c.pos, a)
			continue
		}
		var d *definicao
		var rotulo, valor string
		var temValor bool
		if strings.HasPrefix(a, "--") {
			rotulo, valor, temValor = strings.Cut(a[2:], "=")
			d = c.defs[rotulo]
			rotulo = "--" + rotulo
		} else {
			if len(a) > 2 && a[2] != '=' {
				return fmt.Errorf("flag curta inválida %q (use -x valor)", a)
			}
			rotulo, valor, temValor = strings.Cut(a[1:], "=")
			d = c.curtos[rotulo[0]]
			rotulo = "-" + rotulo
		}
		if d == nil {
			return fmt.Errorf("flag desconhecida %s", rotulo)
		}
		switch {
		case temValor:
		case d.ehBool:
			valor = "true"
		case i+1 < len(args):
			i++
			valor = args[i]
		default:
			return fmt.Errorf("flag %s requer um valor", rotulo)
		}
		if err := d.definir(valor); err != nil {
			return fmt.Errorf("flag %s: %w", rotulo, err)
		}
	}
	return nil
}

// Posicionais devolve os argumentos que não são flags, na ordem em que apareceram.
func (c *Conjunto) Posicionais() []string { return c.pos }

// Uso devolve um texto de ajuda com as flags em ordem alfabética.
func (c *Conjunto) Uso() string {
	nomes := make([]string, 0, len(c.defs))
	for n := range c.defs {
		nomes = append(nomes, n)
	}
	sort.Strings(nomes)
	var b strings.Builder
	fmt.Fprintf(&b, "Uso: %s [opções] [argumentos]\n", c.nome)
	for _, n := range nomes {
		d := c.defs[n]
		if d.curto != 0 {
			fmt.Fprintf(&b, "  -%c, --%s", d.curto, n)
		} else {
			fmt.Fprintf(&b, "      --%s", n)
		}
		fmt.Fprintf(&b, "  %s (padrão: %s)\n", d.uso, d.padrao)
	}
	return b.String()
}
