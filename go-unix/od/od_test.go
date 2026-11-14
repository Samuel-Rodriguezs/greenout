package od

import (
	"bytes"
	"reflect"
	"strings"
	"testing"
)

func TestCaractere(t *testing.T) {
	casos := []struct {
		b    byte
		want string
	}{
		{'a', "a"}, {' ', " "}, {0, `\0`}, {'\n', `\n`}, {'\t', `\t`},
		{'\r', `\r`}, {0x01, "001"}, {0x7f, "177"}, {0xc3, "303"},
	}
	for _, c := range casos {
		if got := Caractere(c.b); got != c.want {
			t.Errorf("Caractere(%#x) = %q, want %q", c.b, got, c.want)
		}
	}
}

func TestDespejar(t *testing.T) {
	casos := []struct {
		nome  string
		dados string
		f     Formato
		want  []string
	}{
		{"vazio", "", Octal, []string{"0000000"}},
		{"octal", "AB", Octal, []string{"0000000 101 102", "0000002"}},
		{"hexa", "AB\n", Hexa, []string{"0000000 41 42 0a", "0000003"}},
		{"chars", "a\n", Chars, []string{"0000000   a  \\n", "0000002"}},
		{"duas linhas", strings.Repeat("a", 17), Hexa, []string{
			"0000000 " + strings.TrimSpace(strings.Repeat("61 ", 16)),
			"0000020 61",
			"0000021",
		}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			got := Despejar([]byte(c.dados), c.f)
			if !reflect.DeepEqual(got, c.want) {
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
		{"padrão octal", nil, "A", "0000000 101\n0000001\n", false},
		{"hexa", []string{"-x"}, "A", "0000000 41\n0000001\n", false},
		{"último formato vence", []string{"-x", "-c"}, "A", "0000000   A\n0000001\n", false},
		{"vazio", nil, "", "0000000\n", false},
		{"argumento inválido", []string{"-z"}, "A", "", true},
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
