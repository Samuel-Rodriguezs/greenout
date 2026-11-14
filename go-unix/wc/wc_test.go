package wc

import (
	"bytes"
	"strings"
	"testing"
)

func TestContar(t *testing.T) {
	casos := []struct {
		nome string
		in   string
		want Contagem
	}{
		{"vazio", "", Contagem{}},
		{"uma linha", "olá mundo\n", Contagem{1, 2, 11, 10}},
		{"sem newline final", "a b c", Contagem{0, 3, 5, 5}},
		{"espaços múltiplos", "  a   b \n\n", Contagem{2, 2, 10, 10}},
		{"utf8", "ção", Contagem{0, 1, 5, 3}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			got, err := Contar(strings.NewReader(c.in))
			if err != nil || got != c.want {
				t.Fatalf("got %+v, %v; want %+v", got, err, c.want)
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
		{"padrão", nil, "a b\nc\n", "2 3 6\n", false},
		{"só linhas", []string{"-l"}, "a\nb\n", "2\n", false},
		{"combinado", []string{"-lw"}, "a b\n", "1 2\n", false},
		{"caracteres", []string{"-m"}, "ção\n", "4\n", false},
		{"bytes", []string{"-c"}, "ção\n", "6\n", false},
		{"opção inválida", []string{"-x"}, "", "", true},
		{"não é opção", []string{"arq"}, "", "", true},
		{"hífen sozinho", []string{"-"}, "", "", true},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			var out bytes.Buffer
			err := Executar(c.args, strings.NewReader(c.in), &out)
			if (err != nil) != c.wantErr {
				t.Fatalf("erro = %v, esperado erro=%v", err, c.wantErr)
			}
			if out.String() != c.want {
				t.Fatalf("got %q, want %q", out.String(), c.want)
			}
		})
	}
}
