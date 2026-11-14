package validacao

import (
	"errors"
	"reflect"
	"testing"
)

type usuario struct {
	Nome  string   `json:"nome" valida:"obrigatorio,min=3,max=10"`
	Email string   `json:"email" valida:"obrigatorio,email"`
	Idade int      `json:"idade" valida:"min=18,max=120"`
	Papel string   `json:"papel" valida:"um_de=admin|user"`
	Tags  []string `json:"tags" valida:"max=2"`
	Livre string
}

func TestValidar(t *testing.T) {
	ok := usuario{Nome: "Ana", Email: "ana@x.com", Idade: 30, Papel: "user", Tags: []string{"a"}}
	casos := []struct {
		nome     string
		entrada  any
		esperado []ErroCampo
	}{
		{"válido", ok, nil},
		{"ponteiro válido", &ok, nil},
		{"tudo vazio", usuario{}, []ErroCampo{
			{"nome", "campo obrigatório"},
			{"email", "campo obrigatório"},
			{"idade", "valor mínimo é 18"},
		}},
		{"nome curto", func() usuario { u := ok; u.Nome = "Al"; return u }(), []ErroCampo{{"nome", "tamanho mínimo é 3"}}},
		{"nome longo", func() usuario { u := ok; u.Nome = "Abcdefghijk"; return u }(), []ErroCampo{{"nome", "tamanho máximo é 10"}}},
		{"email ruim", func() usuario { u := ok; u.Email = "nao-é-email"; return u }(), []ErroCampo{{"email", "e-mail inválido"}}},
		{"idade alta", func() usuario { u := ok; u.Idade = 200; return u }(), []ErroCampo{{"idade", "valor máximo é 120"}}},
		{"papel inválido", func() usuario { u := ok; u.Papel = "root"; return u }(), []ErroCampo{{"papel", "deve ser um de: admin, user"}}},
		{"tags demais", func() usuario { u := ok; u.Tags = []string{"a", "b", "c"}; return u }(), []ErroCampo{{"tags", "tamanho máximo é 2"}}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			err := Validar(c.entrada)
			if c.esperado == nil {
				if err != nil {
					t.Fatalf("erro inesperado: %v", err)
				}
				return
			}
			var es Erros
			if !errors.As(err, &es) {
				t.Fatalf("esperado Erros, obtido %v", err)
			}
			if !reflect.DeepEqual([]ErroCampo(es), c.esperado) {
				t.Errorf("erros %v, esperado %v", es, c.esperado)
			}
		})
	}
}

func TestNaoStruct(t *testing.T) {
	if Validar(42) == nil {
		t.Error("esperado erro para não-struct")
	}
}

func TestRegraDesconhecida(t *testing.T) {
	type x struct {
		A string `valida:"foo"`
	}
	if err := Validar(x{A: "a"}); err == nil {
		t.Error("esperado erro de regra desconhecida")
	}
}

func TestMensagemErros(t *testing.T) {
	e := Erros{{"a", "x"}, {"b", "y"}}
	if e.Error() != "a: x; b: y" {
		t.Errorf("Error() = %q", e.Error())
	}
}
