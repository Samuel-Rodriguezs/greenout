package interp

import (
	"fmt"
	"strconv"
	"strings"

	"greenout/comp/ast"
)

// Valor é qualquer valor em tempo de execução. As operações definidas
// neste arquivo são compartilhadas pelo interpretador e pela VM, garantindo
// a mesma semântica e as mesmas mensagens de erro nos dois.
type Valor interface {
	Tipo() string
	String() string
}

type (
	// Inteiro é um inteiro de 64 bits com aritmética que dá a volta no estouro.
	Inteiro int64
	// Booleano é true ou false.
	Booleano bool
	// Texto é uma sequência de bytes; len e indexação contam bytes.
	Texto string
	// Nulo é o valor de funções sem return e de print.
	Nulo struct{}
)

// Array é uma lista mutável com semântica de referência.
type Array struct{ Elems []Valor }

// Funcao é uma closure do interpretador: corpo mais o ambiente de criação.
type Funcao struct {
	Nome   string
	Params []string
	Corpo  *ast.Bloco
	Env    *Env
}

// Nativa é uma função implementada em Go. Aridade -1 aceita qualquer número
// de argumentos.
type Nativa struct {
	Nome    string
	Aridade int
	Fn      func(args []Valor) (Valor, error)
}

func (Inteiro) Tipo() string  { return "int" }
func (Booleano) Tipo() string { return "bool" }
func (Texto) Tipo() string    { return "texto" }
func (Nulo) Tipo() string     { return "nulo" }
func (*Array) Tipo() string   { return "array" }
func (*Funcao) Tipo() string  { return "função" }
func (*Nativa) Tipo() string  { return "função" }

func (v Inteiro) String() string  { return strconv.FormatInt(int64(v), 10) }
func (v Booleano) String() string { return strconv.FormatBool(bool(v)) }
func (v Texto) String() string    { return string(v) }
func (Nulo) String() string       { return "nulo" }
func (a *Array) String() string   { return repr(a, 0) }
func (f *Funcao) String() string {
	if f.Nome == "" {
		return "<função>"
	}
	return "<função " + f.Nome + ">"
}
func (n *Nativa) String() string { return "<embutido " + n.Nome + ">" }

// Repr devolve a forma de depuração: textos entre aspas, inclusive dentro de arrays.
func Repr(v Valor) string { return repr(v, 0) }

func repr(v Valor, prof int) string {
	switch x := v.(type) {
	case Texto:
		return strconv.Quote(string(x))
	case *Array:
		if prof > 8 {
			return "[...]"
		}
		partes := make([]string, len(x.Elems))
		for i, e := range x.Elems {
			partes[i] = repr(e, prof+1)
		}
		return "[" + strings.Join(partes, ", ") + "]"
	}
	return v.String()
}

// Igual compara dois valores: tipos primitivos por valor, arrays elemento a
// elemento e funções por identidade. Tipos diferentes nunca são iguais.
func Igual(a, b Valor) bool {
	if x, ok := a.(*Array); ok {
		y, ok := b.(*Array)
		if !ok || len(x.Elems) != len(y.Elems) {
			return false
		}
		for i := range x.Elems {
			if !Igual(x.Elems[i], y.Elems[i]) {
				return false
			}
		}
		return true
	}
	return a == b
}

// ComoBool exige um booleano.
func ComoBool(v Valor) (bool, error) {
	if b, ok := v.(Booleano); ok {
		return bool(b), nil
	}
	return false, fmt.Errorf("esperado bool, recebeu %s", v.Tipo())
}

// Prefixar aplica um operador unário (- ou !).
func Prefixar(op string, v Valor) (Valor, error) {
	switch x := v.(type) {
	case Inteiro:
		if op == "-" {
			return -x, nil
		}
	case Booleano:
		if op == "!" {
			return !x, nil
		}
	}
	return nil, fmt.Errorf("operador '%s' não aplicável a %s", op, v.Tipo())
}

// Operar aplica um operador binário aritmético, de comparação ou de igualdade.
// Os operadores lógicos && e || são tratados por quem avalia, por causa do
// curto-circuito.
func Operar(op string, a, b Valor) (Valor, error) {
	switch op {
	case "==":
		return Booleano(Igual(a, b)), nil
	case "!=":
		return Booleano(!Igual(a, b)), nil
	}
	switch x := a.(type) {
	case Inteiro:
		if y, ok := b.(Inteiro); ok {
			return operarInteiros(op, x, y)
		}
	case Texto:
		if y, ok := b.(Texto); ok {
			switch op {
			case "+":
				return x + y, nil
			case "<":
				return Booleano(x < y), nil
			case "<=":
				return Booleano(x <= y), nil
			case ">":
				return Booleano(x > y), nil
			case ">=":
				return Booleano(x >= y), nil
			}
		}
	}
	return nil, fmt.Errorf("operador '%s' não aplicável a %s e %s", op, a.Tipo(), b.Tipo())
}

func operarInteiros(op string, x, y Inteiro) (Valor, error) {
	switch op {
	case "+":
		return x + y, nil
	case "-":
		return x - y, nil
	case "*":
		return x * y, nil
	case "/", "%":
		if y == 0 {
			return nil, fmt.Errorf("divisão por zero")
		}
		if op == "/" {
			return x / y, nil
		}
		return x % y, nil
	case "<":
		return Booleano(x < y), nil
	case "<=":
		return Booleano(x <= y), nil
	case ">":
		return Booleano(x > y), nil
	case ">=":
		return Booleano(x >= y), nil
	}
	return nil, fmt.Errorf("operador '%s' não aplicável a int e int", op)
}

func indice(idx Valor, tam int) (int, error) {
	i, ok := idx.(Inteiro)
	if !ok {
		return 0, fmt.Errorf("índice deve ser int, recebeu %s", idx.Tipo())
	}
	if i < 0 || int64(i) >= int64(tam) {
		return 0, fmt.Errorf("índice %d fora dos limites (tamanho %d)", i, tam)
	}
	return int(i), nil
}

// Indexar lê alvo[idx] em arrays (elemento) e textos (texto de um byte).
func Indexar(alvo, idx Valor) (Valor, error) {
	switch x := alvo.(type) {
	case *Array:
		i, err := indice(idx, len(x.Elems))
		if err != nil {
			return nil, err
		}
		return x.Elems[i], nil
	case Texto:
		i, err := indice(idx, len(x))
		if err != nil {
			return nil, err
		}
		return Texto(x[i : i+1]), nil
	}
	return nil, fmt.Errorf("indexação requer array ou texto, recebeu %s", alvo.Tipo())
}

// AtribuirIndice executa alvo[idx] = v em um array.
func AtribuirIndice(alvo, idx, v Valor) error {
	arr, ok := alvo.(*Array)
	if !ok {
		return fmt.Errorf("atribuição por índice requer array, recebeu %s", alvo.Tipo())
	}
	i, err := indice(idx, len(arr.Elems))
	if err != nil {
		return err
	}
	arr.Elems[i] = v
	return nil
}
