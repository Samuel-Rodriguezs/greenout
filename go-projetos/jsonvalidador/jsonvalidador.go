// Pacote jsonvalidador valida JSON com um parser próprio de descida recursiva,
// sem usar encoding/json. Informa a posição do primeiro erro.
package jsonvalidador

import "fmt"

// ErroSintaxe descreve onde e por que o JSON é inválido.
type ErroSintaxe struct {
	Posicao  int
	Mensagem string
}

func (e *ErroSintaxe) Error() string {
	return fmt.Sprintf("jsonvalidador: %s na posição %d", e.Mensagem, e.Posicao)
}

const profundidadeMax = 200

type validador struct {
	s   string
	pos int
}

func (v *validador) erro(msg string) error { return &ErroSintaxe{v.pos, msg} }

func (v *validador) espacos() {
	for v.pos < len(v.s) && (v.s[v.pos] == ' ' || v.s[v.pos] == '\t' || v.s[v.pos] == '\n' || v.s[v.pos] == '\r') {
		v.pos++
	}
}

func (v *validador) literal(l string) error {
	if len(v.s)-v.pos >= len(l) && v.s[v.pos:v.pos+len(l)] == l {
		v.pos += len(l)
		return nil
	}
	return v.erro("valor inesperado")
}

func (v *validador) valor(prof int) error {
	if prof > profundidadeMax {
		return v.erro("aninhamento excessivo")
	}
	v.espacos()
	if v.pos >= len(v.s) {
		return v.erro("fim inesperado")
	}
	switch c := v.s[v.pos]; {
	case c == '{':
		return v.objeto(prof)
	case c == '[':
		return v.lista(prof)
	case c == '"':
		return v.texto()
	case c == 't':
		return v.literal("true")
	case c == 'f':
		return v.literal("false")
	case c == 'n':
		return v.literal("null")
	case c == '-' || (c >= '0' && c <= '9'):
		return v.numero()
	}
	return v.erro("valor inesperado")
}

func (v *validador) digitos() error {
	ini := v.pos
	for v.pos < len(v.s) && v.s[v.pos] >= '0' && v.s[v.pos] <= '9' {
		v.pos++
	}
	if v.pos == ini {
		return v.erro("dígito esperado")
	}
	return nil
}

func (v *validador) numero() error {
	if v.s[v.pos] == '-' {
		v.pos++
	}
	if v.pos < len(v.s) && v.s[v.pos] == '0' {
		v.pos++
		if v.pos < len(v.s) && v.s[v.pos] >= '0' && v.s[v.pos] <= '9' {
			return v.erro("zero à esquerda")
		}
	} else if err := v.digitos(); err != nil {
		return err
	}
	if v.pos < len(v.s) && v.s[v.pos] == '.' {
		v.pos++
		if err := v.digitos(); err != nil {
			return err
		}
	}
	if v.pos < len(v.s) && (v.s[v.pos] == 'e' || v.s[v.pos] == 'E') {
		v.pos++
		if v.pos < len(v.s) && (v.s[v.pos] == '+' || v.s[v.pos] == '-') {
			v.pos++
		}
		return v.digitos()
	}
	return nil
}

func (v *validador) texto() error {
	v.pos++ // aspas de abertura
	for v.pos < len(v.s) {
		c := v.s[v.pos]
		switch {
		case c == '"':
			v.pos++
			return nil
		case c < 0x20:
			return v.erro("caractere de controle em texto")
		case c == '\\':
			v.pos++
			if v.pos >= len(v.s) {
				return v.erro("escape incompleto")
			}
			if v.s[v.pos] == 'u' {
				for i := 1; i <= 4; i++ {
					if v.pos+i >= len(v.s) || !hex(v.s[v.pos+i]) {
						return v.erro("escape unicode inválido")
					}
				}
				v.pos += 4
			} else if !contem(`"\/bfnrt`, v.s[v.pos]) {
				return v.erro("escape inválido")
			}
		}
		v.pos++
	}
	return v.erro("texto não terminado")
}

func hex(c byte) bool {
	return (c >= '0' && c <= '9') || (c >= 'a' && c <= 'f') || (c >= 'A' && c <= 'F')
}

func contem(s string, c byte) bool {
	for i := 0; i < len(s); i++ {
		if s[i] == c {
			return true
		}
	}
	return false
}

func (v *validador) lista(prof int) error {
	v.pos++
	v.espacos()
	if v.pos < len(v.s) && v.s[v.pos] == ']' {
		v.pos++
		return nil
	}
	for {
		if err := v.valor(prof + 1); err != nil {
			return err
		}
		v.espacos()
		if v.pos >= len(v.s) {
			return v.erro("lista não terminada")
		}
		switch v.s[v.pos] {
		case ',':
			v.pos++
		case ']':
			v.pos++
			return nil
		default:
			return v.erro("esperava ',' ou ']'")
		}
	}
}

func (v *validador) objeto(prof int) error {
	v.pos++
	v.espacos()
	if v.pos < len(v.s) && v.s[v.pos] == '}' {
		v.pos++
		return nil
	}
	for {
		v.espacos()
		if v.pos >= len(v.s) || v.s[v.pos] != '"' {
			return v.erro("chave de texto esperada")
		}
		if err := v.texto(); err != nil {
			return err
		}
		v.espacos()
		if v.pos >= len(v.s) || v.s[v.pos] != ':' {
			return v.erro("esperava ':'")
		}
		v.pos++
		if err := v.valor(prof + 1); err != nil {
			return err
		}
		v.espacos()
		if v.pos >= len(v.s) {
			return v.erro("objeto não terminado")
		}
		switch v.s[v.pos] {
		case ',':
			v.pos++
		case '}':
			v.pos++
			return nil
		default:
			return v.erro("esperava ',' ou '}'")
		}
	}
}

// Validar devolve nil se s for um documento JSON válido, ou *ErroSintaxe.
func Validar(s string) error {
	v := &validador{s: s}
	if err := v.valor(0); err != nil {
		return err
	}
	v.espacos()
	if v.pos != len(v.s) {
		return v.erro("conteúdo após o fim do valor")
	}
	return nil
}
