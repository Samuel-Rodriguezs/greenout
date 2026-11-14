package nl

import (
	"bytes"
	"reflect"
	"strings"
	"testing"
)

func TestNumerar(t *testing.T) {
	casos := []struct {
		nome string
		in   []string
		mod  func(*Opcoes)
		want []string
	}{
		{"padrão", []string{"a", "b"}, func(*Opcoes) {}, []string{"     1\ta", "     2\tb"}},
		{"pula vazias", []string{"a", "", "b"}, func(*Opcoes) {}, []string{"     1\ta", "      \t", "     2\tb"}},
		{"todas as linhas", []string{"a", ""}, func(o *Opcoes) { o.TodasLinhas = true }, []string{"     1\ta", "     2\t"}},
		{"largura e separador", []string{"x"}, func(o *Opcoes) { o.Largura = 3; o.Separador = ": " }, []string{"  1: x"}},
		{"início", []string{"x", "y"}, func(o *Opcoes) { o.Inicio = 10; o.Largura = 2 }, []string{"10\tx", "11\ty"}},
		{"sem linhas", nil, func(*Opcoes) {}, []string{}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			o := PadraoOpcoes()
			c.mod(&o)
			if got := Numerar(c.in, o); !reflect.DeepEqual(got, c.want) {
				t.Fatalf("got %q, want %q", got, c.want)
			}
		})
	}
}

func TestExecutar(t *testing.T) {
	casos := []struct {
		nome    string
		args    []string
		in      string
		want    string
		wantErr bool
	}{
		{"padrão", nil, "a\nb\n", "     1\ta\n     2\tb\n", false},
		{"opções", []string{"-b", "a", "-w", "2", "-s", "|", "-v", "5"}, "a\n\n", " 5|a\n 6|\n", false},
		{"vazio", nil, "", "", false},
		{"opção sem valor", []string{"-w"}, "a\n", "", true},
		{"largura inválida", []string{"-w", "0"}, "a\n", "", true},
		{"estilo inválido", []string{"-b", "x"}, "a\n", "", true},
		{"início inválido", []string{"-v", "x"}, "a\n", "", true},
		{"opção desconhecida", []string{"-z", "1"}, "a\n", "", true},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			var out bytes.Buffer
			err := Executar(c.args, strings.NewReader(c.in), &out)
			if (err != nil) != c.wantErr || out.String() != c.want {
				t.Fatalf("got %q, %v; want %q (erro=%v)", out.String(), err, c.want, c.wantErr)
			}
		})
	}
}
