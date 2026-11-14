package head

import (
	"bytes"
	"fmt"
	"reflect"
	"strings"
	"testing"
)

func TestPrimeiras(t *testing.T) {
	l := []string{"1", "2", "3", "4"}
	casos := []struct {
		nome string
		n    int
		want []string
	}{
		{"duas", 2, []string{"1", "2"}},
		{"zero", 0, []string{}},
		{"maior que total", 10, l},
		{"negativo", -1, []string{"1", "2", "3"}},
		{"negativo excessivo", -9, []string{}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			got := Primeiras(l, c.n)
			if !reflect.DeepEqual(got, c.want) {
				t.Fatalf("got %v, want %v", got, c.want)
			}
		})
	}
}

func TestParseN(t *testing.T) {
	casos := []struct {
		nome    string
		args    []string
		want    int
		wantErr bool
	}{
		{"padrão", nil, 10, false},
		{"separado", []string{"-n", "3"}, 3, false},
		{"colado", []string{"-n5"}, 5, false},
		{"curto", []string{"-7"}, 7, false},
		{"negativo", []string{"-n", "-2"}, -2, false},
		{"sem valor", []string{"-n"}, 0, true},
		{"não numérico", []string{"-nabc"}, 0, true},
		{"argumento solto", []string{"x"}, 0, true},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			got, err := ParseN(c.args)
			if (err != nil) != c.wantErr || got != c.want {
				t.Fatalf("got %d, %v; want %d (erro=%v)", got, err, c.want, c.wantErr)
			}
		})
	}
}

func TestExecutar(t *testing.T) {
	var dozeLinhas strings.Builder
	for i := 1; i <= 12; i++ {
		fmt.Fprintf(&dozeLinhas, "%d\n", i)
	}
	casos := []struct {
		nome    string
		args    []string
		in      string
		want    string
		wantErr bool
	}{
		{"padrão 10", nil, dozeLinhas.String(), "1\n2\n3\n4\n5\n6\n7\n8\n9\n10\n", false},
		{"n=2", []string{"-n", "2"}, "a\nb\nc\n", "a\nb\n", false},
		{"sem newline final", []string{"-n", "1"}, "a\nb", "a\n", false},
		{"vazio", nil, "", "", false},
		{"erro", []string{"-n", "x"}, "a\n", "", true},
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
