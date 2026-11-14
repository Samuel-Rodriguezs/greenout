package sort

import (
	"bytes"
	"reflect"
	"strings"
	"testing"
)

func TestOrdenar(t *testing.T) {
	casos := []struct {
		nome string
		in   []string
		o    Opcoes
		want []string
	}{
		{"léxico", []string{"b", "a", "c"}, Opcoes{}, []string{"a", "b", "c"}},
		{"reverso", []string{"b", "a", "c"}, Opcoes{Reverso: true}, []string{"c", "b", "a"}},
		{"numérico", []string{"10", "9", "100", "-5"}, Opcoes{Numerico: true}, []string{"-5", "9", "10", "100"}},
		{"numérico com texto", []string{"2 b", "x", "1 a"}, Opcoes{Numerico: true}, []string{"x", "1 a", "2 b"}},
		{"único", []string{"b", "a", "b", "a"}, Opcoes{Unico: true}, []string{"a", "b"}},
		{"ignorar caixa", []string{"b", "A", "C"}, Opcoes{IgnorarCaixa: true}, []string{"A", "b", "C"}},
		{"vazio", nil, Opcoes{}, nil},
		{"único reverso", []string{"a", "c", "a", "b"}, Opcoes{Unico: true, Reverso: true}, []string{"c", "b", "a"}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			got := Ordenar(c.in, c.o)
			if len(got) == 0 && len(c.want) == 0 {
				return
			}
			if !reflect.DeepEqual(got, c.want) {
				t.Fatalf("got %v, want %v", got, c.want)
			}
		})
	}
}

func TestOrdenarNaoAlteraEntrada(t *testing.T) {
	in := []string{"b", "a"}
	Ordenar(in, Opcoes{})
	if in[0] != "b" {
		t.Fatal("entrada foi modificada")
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
		{"básico", nil, "b\na\n", "a\nb\n", false},
		{"sem newline final", nil, "b\na", "a\nb\n", false},
		{"vazio", nil, "", "", false},
		{"-nr", []string{"-nr"}, "1\n3\n2\n", "3\n2\n1\n", false},
		{"opção inválida", []string{"-k"}, "", "", true},
		{"argumento solto", []string{"x"}, "", "", true},
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
