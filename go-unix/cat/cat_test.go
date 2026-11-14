package cat

import (
	"bytes"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestFormatar(t *testing.T) {
	casos := []struct {
		nome string
		in   string
		o    Opcoes
		want string
	}{
		{"vazio", "", Opcoes{Numerar: true}, ""},
		{"sem opções", "a\nb\n", Opcoes{}, "a\nb\n"},
		{"sem newline final", "a\nb", Opcoes{}, "a\nb"},
		{"numerar", "a\nb\n", Opcoes{Numerar: true}, "     1\ta\n     2\tb\n"},
		{"fim de linha", "a\n\n", Opcoes{FimLinha: true}, "a$\n$\n"},
		{"comprimir", "a\n\n\n\nb\n", Opcoes{Comprimir: true}, "a\n\nb\n"},
		{"comprimir e numerar", "a\n\n\nb\n", Opcoes{Comprimir: true, Numerar: true}, "     1\ta\n     2\t\n     3\tb\n"},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := Formatar(c.in, c.o); got != c.want {
				t.Fatalf("got %q, want %q", got, c.want)
			}
		})
	}
}

func TestExecutar(t *testing.T) {
	dir := t.TempDir()
	arq := filepath.Join(dir, "a.txt")
	if err := os.WriteFile(arq, []byte("do arquivo\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	casos := []struct {
		nome    string
		args    []string
		in      string
		want    string
		wantErr bool
	}{
		{"stdin implícita", nil, "oi\n", "oi\n", false},
		{"stdin com hífen", []string{"-"}, "oi\n", "oi\n", false},
		{"arquivo", []string{arq}, "ignorado", "do arquivo\n", false},
		{"arquivo e stdin", []string{arq, "-"}, "oi\n", "do arquivo\noi\n", false},
		{"numerar", []string{"-n", arq}, "", "     1\tdo arquivo\n", false},
		{"arquivo inexistente", []string{filepath.Join(dir, "nao.txt")}, "", "", true},
		{"opção inválida", []string{"-z"}, "", "", true},
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
