// Pacote validacao valida structs por tags, por exemplo:
//
//	type Usuario struct {
//	    Nome  string `json:"nome"  valida:"obrigatorio,min=3,max=20"`
//	    Email string `json:"email" valida:"obrigatorio,email"`
//	    Idade int    `json:"idade" valida:"min=18,max=120"`
//	}
//
// Regras: obrigatorio, min=N, max=N (tamanho para strings/slices, valor para
// números), email, um_de=a|b|c.
package validacao

import (
	"fmt"
	"net/mail"
	"reflect"
	"strconv"
	"strings"
)

// ErroCampo descreve uma violação.
type ErroCampo struct {
	Campo    string `json:"campo"`
	Mensagem string `json:"mensagem"`
}

// Erros é a lista de violações e implementa error.
type Erros []ErroCampo

func (e Erros) Error() string {
	partes := make([]string, len(e))
	for i, x := range e {
		partes[i] = x.Campo + ": " + x.Mensagem
	}
	return strings.Join(partes, "; ")
}

func nomeJSON(f reflect.StructField) string {
	if n, _, _ := strings.Cut(f.Tag.Get("json"), ","); n != "" && n != "-" {
		return n
	}
	return f.Name
}

// Validar verifica v (struct ou ponteiro para struct). Retorna nil se válido.
func Validar(v any) error {
	val := reflect.Indirect(reflect.ValueOf(v))
	if val.Kind() != reflect.Struct {
		return fmt.Errorf("validacao: esperado struct, recebido %s", val.Kind())
	}
	var erros Erros
	t := val.Type()
	for i := 0; i < t.NumField(); i++ {
		campo := t.Field(i)
		tag := campo.Tag.Get("valida")
		if tag == "" || !campo.IsExported() {
			continue
		}
		nome := nomeJSON(campo)
		fv := val.Field(i)
		for _, regra := range strings.Split(tag, ",") {
			if msg := aplicar(strings.TrimSpace(regra), fv); msg != "" {
				erros = append(erros, ErroCampo{nome, msg})
				break
			}
		}
	}
	if len(erros) == 0 {
		return nil
	}
	return erros
}

func tamanhoOuValor(fv reflect.Value) (float64, string) {
	switch fv.Kind() {
	case reflect.String, reflect.Slice, reflect.Map:
		return float64(fv.Len()), "tamanho"
	case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
		return float64(fv.Int()), "valor"
	case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64:
		return float64(fv.Uint()), "valor"
	case reflect.Float32, reflect.Float64:
		return fv.Float(), "valor"
	}
	return 0, "valor"
}

func aplicar(regra string, fv reflect.Value) string {
	nome, arg, _ := strings.Cut(regra, "=")
	switch nome {
	case "obrigatorio":
		if fv.IsZero() {
			return "campo obrigatório"
		}
	case "min", "max":
		n, err := strconv.ParseFloat(arg, 64)
		if err != nil {
			return "regra inválida: " + regra
		}
		// Campos vazios só são cobrados por "obrigatorio".
		if fv.IsZero() && fv.Kind() == reflect.String {
			return ""
		}
		x, rot := tamanhoOuValor(fv)
		if nome == "min" && x < n {
			return fmt.Sprintf("%s mínimo é %s", rot, arg)
		}
		if nome == "max" && x > n {
			return fmt.Sprintf("%s máximo é %s", rot, arg)
		}
	case "email":
		if s := fv.String(); fv.Kind() == reflect.String && s != "" {
			if a, err := mail.ParseAddress(s); err != nil || a.Address != s {
				return "e-mail inválido"
			}
		}
	case "um_de":
		if s := fmt.Sprint(fv.Interface()); s != "" {
			for _, op := range strings.Split(arg, "|") {
				if op == s {
					return ""
				}
			}
			return "deve ser um de: " + strings.ReplaceAll(arg, "|", ", ")
		}
	default:
		return "regra desconhecida: " + nome
	}
	return ""
}
