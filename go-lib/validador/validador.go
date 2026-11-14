// Pacote validador valida structs a partir de tags `valida:"..."` usando reflect.
//
// Regras suportadas (separadas por vírgula):
//
//	obrigatorio  valor não pode ser o zero do tipo
//	min=N        string/slice/map: tamanho mínimo; números: valor mínimo
//	max=N        idem, máximo
//	email        string com formato básico de e-mail
//	em=a|b|c     valor deve ser um dos listados
//
// Campos opcionais vazios (zero) pulam todas as regras exceto "obrigatorio".
// Structs aninhadas são validadas recursivamente (nomes como "Pai.Filho").
package validador

import (
	"fmt"
	"reflect"
	"regexp"
	"strconv"
	"strings"
	"unicode/utf8"
)

var reEmail = regexp.MustCompile(`^[^@\s]+@[^@\s]+\.[^@\s]+$`)

// ErroCampo descreve uma violação em um campo.
type ErroCampo struct {
	Campo    string
	Regra    string
	Mensagem string
}

func (e ErroCampo) Error() string { return e.Campo + ": " + e.Mensagem }

// Erros agrupa todas as violações encontradas.
type Erros []ErroCampo

func (e Erros) Error() string {
	partes := make([]string, len(e))
	for i, x := range e {
		partes[i] = x.Error()
	}
	return strings.Join(partes, "; ")
}

// Validar valida v (struct ou ponteiro para struct). Retorna nil se tudo estiver ok,
// ou um valor do tipo Erros.
func Validar(v any) error {
	rv := reflect.ValueOf(v)
	for rv.Kind() == reflect.Pointer {
		if rv.IsNil() {
			return Erros{{Campo: "", Regra: "tipo", Mensagem: "ponteiro nulo"}}
		}
		rv = rv.Elem()
	}
	if rv.Kind() != reflect.Struct {
		return Erros{{Campo: "", Regra: "tipo", Mensagem: "esperava struct"}}
	}
	var erros Erros
	validarStruct(rv, "", &erros)
	if len(erros) == 0 {
		return nil
	}
	return erros
}

func validarStruct(rv reflect.Value, prefixo string, erros *Erros) {
	rt := rv.Type()
	for i := 0; i < rt.NumField(); i++ {
		sf := rt.Field(i)
		if !sf.IsExported() {
			continue
		}
		campo := prefixo + sf.Name
		fv := rv.Field(i)
		if fv.Kind() == reflect.Struct {
			validarStruct(fv, campo+".", erros)
			continue
		}
		tag, ok := sf.Tag.Lookup("valida")
		if !ok || tag == "" {
			continue
		}
		validarCampo(campo, fv, tag, erros)
	}
}

func validarCampo(campo string, fv reflect.Value, tag string, erros *Erros) {
	falha := func(regra, msg string) {
		*erros = append(*erros, ErroCampo{Campo: campo, Regra: regra, Mensagem: msg})
	}
	regras := strings.Split(tag, ",")
	obrigatorio := false
	for _, r := range regras {
		if strings.TrimSpace(r) == "obrigatorio" {
			obrigatorio = true
		}
	}
	if fv.IsZero() {
		if obrigatorio {
			falha("obrigatorio", "campo obrigatório")
		}
		return
	}
	for _, r := range regras {
		nome, arg, _ := strings.Cut(strings.TrimSpace(r), "=")
		switch nome {
		case "obrigatorio", "":
		case "min", "max":
			lim, err := strconv.ParseFloat(arg, 64)
			if err != nil {
				falha("tag", fmt.Sprintf("argumento inválido em %q", r))
				continue
			}
			medida, ok := medir(fv)
			if !ok {
				falha("tag", fmt.Sprintf("regra %s não se aplica ao tipo %s", nome, fv.Type()))
				continue
			}
			if nome == "min" && medida < lim {
				falha("min", fmt.Sprintf("deve ser no mínimo %s", arg))
			}
			if nome == "max" && medida > lim {
				falha("max", fmt.Sprintf("deve ser no máximo %s", arg))
			}
		case "email":
			if fv.Kind() != reflect.String || !reEmail.MatchString(fv.String()) {
				falha("email", "e-mail inválido")
			}
		case "em":
			valor := fmt.Sprint(fv.Interface())
			if !contem(strings.Split(arg, "|"), valor) {
				falha("em", "deve ser um de: "+strings.ReplaceAll(arg, "|", ", "))
			}
		default:
			falha("tag", fmt.Sprintf("regra desconhecida %q", nome))
		}
	}
}

// medir devolve o tamanho (string/slice/map) ou o valor numérico do campo.
func medir(fv reflect.Value) (float64, bool) {
	switch fv.Kind() {
	case reflect.String:
		return float64(utf8.RuneCountInString(fv.String())), true
	case reflect.Slice, reflect.Map, reflect.Array:
		return float64(fv.Len()), true
	case reflect.Int, reflect.Int8, reflect.Int16, reflect.Int32, reflect.Int64:
		return float64(fv.Int()), true
	case reflect.Uint, reflect.Uint8, reflect.Uint16, reflect.Uint32, reflect.Uint64:
		return float64(fv.Uint()), true
	case reflect.Float32, reflect.Float64:
		return fv.Float(), true
	}
	return 0, false
}

func contem(lista []string, v string) bool {
	for _, x := range lista {
		if x == v {
			return true
		}
	}
	return false
}
