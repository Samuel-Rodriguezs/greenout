package tail

import (
	"bytes"
	"reflect"
	"strings"
	"testing"
)

func TestUltimas(t *testing.T) {
	l := []string{"1", "2", "3", "4"}
	casos := []struct {
		nome string
		n    int
		want []string
	}{
		{"duas", 2, []string{"3", "4"}},
		{"zero", 0, []string{}},
		{"maior que total", 9, l},
		{"negativo vira zero", -3, []string{}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			got := Ultimas(l, c.n)
			if !reflect.DeepEqual(got, c.want) {
				t.Fatalf("got %v, want %v", got, c.want)
			}
		})
	}
}

func TestApartirDe(t *testing.T) {
	l := []string{"1", "2", "3"}
	casos := []struct {
		nome string
		k    int
		want []string
	}{
		{"da segunda", 2, []string{"2", "3"}},
		{"da primeira", 1, l},
		{"zero vira um", 0, l},
		{"além do fim", 9, []string{}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			got := ApartirDe(l, c.k)
			if !reflect.DeepEqual(got, c.want) {
				t.Fatalf("got %v, want %v", got, c.want)
			}
		})
	}
}

func TestExecutar(t *testing.T) {
	in := "a\nb\nc\nd\n"
	casos := []struct {
		nome    string
		args    []string
		in      string
		want    string
		wantErr bool
	}{
		{"padrão", nil, in, "a\nb\nc\nd\n", false},
		{"n=2", []string{"-n", "2"}, in, "c\nd\n", false},
		{"colado", []string{"-n1"}, in, "d\n", false},
		{"mais K", []string{"-n", "+3"}, in, "c\nd\n", false},
		{"sem newline final", []string{"-n", "1"}, "a\nb", "b\n", false},
		{"vazio", nil, "", "", false},
		{"sem valor", []string{"-n"}, in, "", true},
		{"inválido", []string{"-n", "x"}, in, "", true},
		{"negativo", []string{"-n", "-1"}, in, "", true},
		{"argumento solto", []string{"arq"}, in, "", true},
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
