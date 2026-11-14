package jsonvalidador

import (
	"encoding/json"
	"errors"
	"strings"
	"testing"
)

func TestValidos(t *testing.T) {
	casos := []string{
		`null`, `true`, `false`, `0`, `-1`, `3.14`, `1e10`, `-2.5E-3`, `"abc"`,
		`"esc \" \\ \/ \b \f \n \r \t é"`, `[]`, `{}`, `[1, 2, 3]`,
		`{"a": 1, "b": [true, null, {"c": "d"}]}`, "  \n\t[ ]  ", `"acentuação ç"`,
	}
	for _, c := range casos {
		t.Run(c, func(t *testing.T) {
			if err := Validar(c); err != nil {
				t.Errorf("deveria ser válido: %v", err)
			}
			if !json.Valid([]byte(c)) {
				t.Error("divergência com encoding/json")
			}
		})
	}
}

func TestInvalidos(t *testing.T) {
	casos := []struct {
		nome, json string
		pos        int
	}{
		{"vazio", ``, 0},
		{"virgula sobrando", `[1,]`, 3},
		{"chave sem aspas", `{a: 1}`, 1},
		{"sem dois pontos", `{"a" 1}`, 5},
		{"aspas simples", `'a'`, 0},
		{"zero a esquerda", `01`, 1},
		{"ponto sem digito", `1.`, 2},
		{"expoente sem digito", `1e`, 2},
		{"menos sozinho", `-`, 1},
		{"texto aberto", `"abc`, 4},
		{"escape invalido", `"\x"`, 2},
		{"unicode curto", `"\u12"`, 2},
		{"controle em texto", "\"a\nb\"", 2},
		{"lista aberta", `[1, 2`, 5},
		{"objeto aberto", `{"a": 1`, 7},
		{"lixo no fim", `{} x`, 3},
		{"literal errado", `tru`, 0},
		{"dois valores", `1 2`, 2},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			err := Validar(c.json)
			var es *ErroSintaxe
			if !errors.As(err, &es) {
				t.Fatalf("esperava *ErroSintaxe, veio %v", err)
			}
			if es.Posicao != c.pos {
				t.Errorf("posição = %d, esperada %d (%s)", es.Posicao, c.pos, es.Mensagem)
			}
			if json.Valid([]byte(c.json)) {
				t.Error("divergência com encoding/json")
			}
		})
	}
}

func TestProfundidade(t *testing.T) {
	ok := strings.Repeat("[", 100) + strings.Repeat("]", 100)
	if err := Validar(ok); err != nil {
		t.Errorf("100 níveis deveria passar: %v", err)
	}
	ruim := strings.Repeat("[", 500) + strings.Repeat("]", 500)
	if err := Validar(ruim); err == nil {
		t.Error("500 níveis deveria falhar")
	}
}
