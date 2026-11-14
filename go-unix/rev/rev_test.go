package rev

import (
	"bytes"
	"errors"
	"strings"
	"testing"
)

func TestInverter(t *testing.T) {
	casos := []struct{ nome, in, want string }{
		{"vazio", "", ""},
		{"um caractere", "a", "a"},
		{"simples", "abc", "cba"},
		{"palíndromo", "arara", "arara"},
		{"utf8", "ação", "oãça"},
		{"espaços", "a b", "b a"},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := Inverter(c.in); got != c.want {
				t.Fatalf("got %q, want %q", got, c.want)
			}
		})
	}
}

type leitorQuebrado struct{}

func (leitorQuebrado) Read([]byte) (int, error) { return 0, errors.New("falha de leitura") }

func TestExecutar(t *testing.T) {
	casos := []struct {
		nome    string
		args    []string
		in      string
		want    string
		wantErr bool
	}{
		{"linhas", nil, "abc\ndef\n", "cba\nfed\n", false},
		{"sem newline final", nil, "abc", "cba", false},
		{"linha vazia", nil, "a\n\nb\n", "a\n\nb\n", false},
		{"vazio", nil, "", "", false},
		{"argumento", []string{"x"}, "", "", true},
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
	if err := Executar(nil, leitorQuebrado{}, &bytes.Buffer{}); err == nil {
		t.Fatal("esperava erro de leitura")
	}
}
