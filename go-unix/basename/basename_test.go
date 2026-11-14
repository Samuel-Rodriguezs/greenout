package basename

import (
	"bytes"
	"strings"
	"testing"
)

func TestBase(t *testing.T) {
	casos := []struct{ nome, caminho, sufixo, want string }{
		{"simples", "a/b/c.txt", "", "c.txt"},
		{"sem diretório", "c.txt", "", "c.txt"},
		{"barras finais", "a/b/", "", "b"},
		{"raiz", "/", "", "/"},
		{"várias barras", "///", "", "/"},
		{"vazio", "", "", ""},
		{"com sufixo", "a/b/c.txt", ".txt", "c"},
		{"sufixo não casa", "c.txt", ".go", "c.txt"},
		{"sufixo igual ao nome", ".txt", ".txt", ".txt"},
		{"absoluto", "/usr/bin/go", "", "go"},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := Base(c.caminho, c.sufixo); got != c.want {
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
		{"um operando", []string{"/a/b.go"}, "b.go\n", false},
		{"com sufixo", []string{"/a/b.go", ".go"}, "b\n", false},
		{"sem operando", nil, "", true},
		{"operando extra", []string{"a", "b", "c"}, "", true},
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
