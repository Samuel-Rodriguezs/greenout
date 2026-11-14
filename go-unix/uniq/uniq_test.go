package uniq

import (
	"bytes"
	"reflect"
	"strings"
	"testing"
)

func TestAgrupar(t *testing.T) {
	casos := []struct {
		nome   string
		in     []string
		ignora bool
		want   []Grupo
	}{
		{"vazio", nil, false, nil},
		{"adjacentes", []string{"a", "a", "b", "a"}, false, []Grupo{{"a", 2}, {"b", 1}, {"a", 1}}},
		{"caixa distinta", []string{"a", "A"}, false, []Grupo{{"a", 1}, {"A", 1}}},
		{"ignorar caixa", []string{"a", "A", "a"}, true, []Grupo{{"a", 3}}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			got := Agrupar(c.in, c.ignora)
			if !reflect.DeepEqual(got, c.want) {
				t.Fatalf("got %v, want %v", got, c.want)
			}
		})
	}
}

func TestExecutar(t *testing.T) {
	in := "a\na\nb\nc\nc\nc\n"
	casos := []struct {
		nome    string
		args    []string
		in      string
		want    string
		wantErr bool
	}{
		{"padrão", nil, in, "a\nb\nc\n", false},
		{"contar", []string{"-c"}, in, "      2 a\n      1 b\n      3 c\n", false},
		{"repetidas", []string{"-d"}, in, "a\nc\n", false},
		{"únicas", []string{"-u"}, in, "b\n", false},
		{"ignorar caixa", []string{"-i"}, "A\na\n", "A\n", false},
		{"vazio", nil, "", "", false},
		{"d e u juntos", []string{"-d", "-u"}, in, "", true},
		{"opção inválida", []string{"-z"}, in, "", true},
		{"argumento solto", []string{"x"}, in, "", true},
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
