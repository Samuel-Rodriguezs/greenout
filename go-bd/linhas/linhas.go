// Pacote linhas serializa linhas de tabela com tipos. Cada linha é
// codificada como um bitmap de nulos (1 bit por coluna, LSB primeiro)
// seguido dos valores não nulos na ordem das colunas:
//
//	Inteiro   varint com sinal (zigzag)
//	Real      8 bytes IEEE-754 little endian
//	Texto     uvarint do tamanho + bytes UTF-8
//	Booleano  1 byte (0 ou 1)
//	Bytes     uvarint do tamanho + bytes
//
// Valores Go aceitos na codificação: qualquer tipo inteiro, float32/float64,
// string, bool e []byte; a decodificação devolve int64, float64, string,
// bool, []byte ou nil.
package linhas

import (
	"encoding/binary"
	"errors"
	"fmt"
	"math"
	"unicode/utf8"
)

// Tipo é o tipo de uma coluna.
type Tipo uint8

const (
	Inteiro Tipo = iota + 1
	Real
	Texto
	Booleano
	Bytes
)

var nomesTipo = map[Tipo]string{Inteiro: "INTEIRO", Real: "REAL", Texto: "TEXTO", Booleano: "BOOLEANO", Bytes: "BYTES"}

func (t Tipo) String() string {
	if n, ok := nomesTipo[t]; ok {
		return n
	}
	return fmt.Sprintf("TIPO(%d)", uint8(t))
}

// MarshalText permite serializar o tipo como texto (JSON legível).
func (t Tipo) MarshalText() ([]byte, error) {
	if _, ok := nomesTipo[t]; !ok {
		return nil, fmt.Errorf("%w: %d", ErrTipoInvalido, uint8(t))
	}
	return []byte(t.String()), nil
}

// UnmarshalText é o inverso de MarshalText.
func (t *Tipo) UnmarshalText(b []byte) error {
	for k, n := range nomesTipo {
		if n == string(b) {
			*t = k
			return nil
		}
	}
	return fmt.Errorf("%w: %q", ErrTipoInvalido, b)
}

var (
	// ErrEsquema indica esquema inválido.
	ErrEsquema = errors.New("linhas: esquema inválido")
	// ErrTipoInvalido indica tipo de coluna desconhecido.
	ErrTipoInvalido = errors.New("linhas: tipo de coluna inválido")
	// ErrValor indica valor incompatível com a coluna.
	ErrValor = errors.New("linhas: valor incompatível com a coluna")
	// ErrNulo indica nulo em coluna não nulável.
	ErrNulo = errors.New("linhas: nulo em coluna não nulável")
	// ErrCorrompida indica bytes que não formam uma linha válida do esquema.
	ErrCorrompida = errors.New("linhas: linha corrompida")
)

// Coluna descreve uma coluna da tabela.
type Coluna struct {
	Nome    string `json:"nome"`
	Tipo    Tipo   `json:"tipo"`
	Nulavel bool   `json:"nulavel"`
}

// Esquema é a lista ordenada de colunas.
type Esquema struct {
	Colunas []Coluna `json:"colunas"`
}

// NovoEsquema valida e cria um esquema.
func NovoEsquema(cols ...Coluna) (Esquema, error) {
	e := Esquema{Colunas: append([]Coluna(nil), cols...)}
	if err := e.Validar(); err != nil {
		return Esquema{}, err
	}
	return e, nil
}

// Validar confere nomes (não vazios e únicos) e tipos.
func (e Esquema) Validar() error {
	if len(e.Colunas) == 0 {
		return fmt.Errorf("%w: sem colunas", ErrEsquema)
	}
	vistos := map[string]bool{}
	for i, c := range e.Colunas {
		if c.Nome == "" {
			return fmt.Errorf("%w: coluna %d sem nome", ErrEsquema, i)
		}
		if vistos[c.Nome] {
			return fmt.Errorf("%w: coluna %q repetida", ErrEsquema, c.Nome)
		}
		vistos[c.Nome] = true
		if _, ok := nomesTipo[c.Tipo]; !ok {
			return fmt.Errorf("%w: coluna %q: %v", ErrEsquema, c.Nome, ErrTipoInvalido)
		}
	}
	return nil
}

// Indice devolve a posição da coluna pelo nome, ou -1.
func (e Esquema) Indice(nome string) int {
	for i, c := range e.Colunas {
		if c.Nome == nome {
			return i
		}
	}
	return -1
}

func inteiro(v any) (int64, bool) {
	switch n := v.(type) {
	case int:
		return int64(n), true
	case int8:
		return int64(n), true
	case int16:
		return int64(n), true
	case int32:
		return int64(n), true
	case int64:
		return n, true
	case uint8:
		return int64(n), true
	case uint16:
		return int64(n), true
	case uint32:
		return int64(n), true
	}
	return 0, false
}

// Codificar serializa uma linha; valores[i] corresponde à coluna i, e nil é nulo.
func (e Esquema) Codificar(valores []any) ([]byte, error) {
	if len(valores) != len(e.Colunas) {
		return nil, fmt.Errorf("%w: %d valores para %d colunas", ErrValor, len(valores), len(e.Colunas))
	}
	n := len(e.Colunas)
	out := make([]byte, (n+7)/8)
	for i, c := range e.Colunas {
		v := valores[i]
		if v == nil {
			if !c.Nulavel {
				return nil, fmt.Errorf("%w: coluna %q", ErrNulo, c.Nome)
			}
			out[i/8] |= 1 << (i % 8)
			continue
		}
		var ok bool
		switch c.Tipo {
		case Inteiro:
			var x int64
			if x, ok = inteiro(v); ok {
				out = binary.AppendVarint(out, x)
			}
		case Real:
			var f float64
			switch x := v.(type) {
			case float64:
				f, ok = x, true
			case float32:
				f, ok = float64(x), true
			}
			if ok {
				out = binary.LittleEndian.AppendUint64(out, math.Float64bits(f))
			}
		case Texto:
			var s string
			if s, ok = v.(string); ok {
				if !utf8.ValidString(s) {
					return nil, fmt.Errorf("%w: coluna %q: texto não é UTF-8 válido", ErrValor, c.Nome)
				}
				out = binary.AppendUvarint(out, uint64(len(s)))
				out = append(out, s...)
			}
		case Booleano:
			var b bool
			if b, ok = v.(bool); ok {
				if b {
					out = append(out, 1)
				} else {
					out = append(out, 0)
				}
			}
		case Bytes:
			var b []byte
			if b, ok = v.([]byte); ok {
				out = binary.AppendUvarint(out, uint64(len(b)))
				out = append(out, b...)
			}
		}
		if !ok {
			return nil, fmt.Errorf("%w: coluna %q (%v) recebeu %T", ErrValor, c.Nome, c.Tipo, v)
		}
	}
	return out, nil
}

// Decodificar lê uma linha completa; sobra ou falta de bytes é ErrCorrompida.
func (e Esquema) Decodificar(b []byte) ([]any, error) {
	n := len(e.Colunas)
	tamMapa := (n + 7) / 8
	if len(b) < tamMapa {
		return nil, fmt.Errorf("%w: bitmap truncado", ErrCorrompida)
	}
	mapa, b := b[:tamMapa], b[tamMapa:]
	// bits além das colunas devem ser zero
	if resto := n % 8; resto != 0 && mapa[tamMapa-1]>>resto != 0 {
		return nil, fmt.Errorf("%w: bits extras no bitmap", ErrCorrompida)
	}
	vals := make([]any, n)
	for i, c := range e.Colunas {
		if mapa[i/8]&(1<<(i%8)) != 0 {
			if !c.Nulavel {
				return nil, fmt.Errorf("%w: coluna %q nula mas não nulável", ErrCorrompida, c.Nome)
			}
			continue
		}
		switch c.Tipo {
		case Inteiro:
			x, k := binary.Varint(b)
			if k <= 0 {
				return nil, fmt.Errorf("%w: coluna %q", ErrCorrompida, c.Nome)
			}
			vals[i], b = x, b[k:]
		case Real:
			if len(b) < 8 {
				return nil, fmt.Errorf("%w: coluna %q", ErrCorrompida, c.Nome)
			}
			vals[i], b = math.Float64frombits(binary.LittleEndian.Uint64(b)), b[8:]
		case Booleano:
			if len(b) < 1 || b[0] > 1 {
				return nil, fmt.Errorf("%w: coluna %q", ErrCorrompida, c.Nome)
			}
			vals[i], b = b[0] == 1, b[1:]
		case Texto, Bytes:
			tam, k := binary.Uvarint(b)
			if k <= 0 || tam > uint64(len(b)-k) {
				return nil, fmt.Errorf("%w: coluna %q", ErrCorrompida, c.Nome)
			}
			dado := b[k : k+int(tam)]
			b = b[k+int(tam):]
			if c.Tipo == Texto {
				if !utf8.Valid(dado) {
					return nil, fmt.Errorf("%w: coluna %q: UTF-8 inválido", ErrCorrompida, c.Nome)
				}
				vals[i] = string(dado)
			} else {
				vals[i] = append([]byte{}, dado...)
			}
		}
	}
	if len(b) != 0 {
		return nil, fmt.Errorf("%w: %d bytes sobrando", ErrCorrompida, len(b))
	}
	return vals, nil
}
