package dirname

import (
	"bytes"
	"strings"
	"testing"
)

func TestDir(t *testing.T) {
	casos := []struct{ nome, in, want string }{
		{"simples", "a/b/c", "a/b"},
		{"sem barra", "arquivo", "."},
		{"vazio", "", "."},
		{"raiz", "/", "/"},
		{"filho da raiz", "/usr", "/"},
		{"barra final", "a/b/", "a"},
		{"barras duplicadas", "a//b", "a"},
		{"várias barras finais", "/a/b///", "/a"},
		{"só barras", "///", "/"},
		{"relativo", "./x", "."},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := Dir(c.in); got != c.want {
				t.Fatalf("got %q, want %q", got, c.want)
			}
		})
	}
}

func TestExecutar(t *testing.T) {
	casos := []struct {
		nome    string
		args    []string
		want    string
		wantErr bool
	}{
		{"um", []string{"/a/b"}, "/a\n", false},
		{"vários", []string{"a/b", "c"}, "a\n.\n", false},
		{"sem operando", nil, "", true},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			var out bytes.Buffer
			err := Executar(c.args, strings.NewReader(""), &out)
			if (err != nil) != c.wantErr || out.String() != c.want {
				t.Fatalf("got %q, %v; want %q (erro=%v)", out.String(), err, c.want, c.wantErr)
			}
		})
	}
}
