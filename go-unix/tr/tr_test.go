package tr

import (
	"bytes"
	"strings"
	"testing"
)

func TestExpandir(t *testing.T) {
	casos := []struct {
		nome    string
		in      string
		want    string
		wantErr bool
	}{
		{"literal", "abc", "abc", false},
		{"faixa", "a-e", "abcde", false},
		{"faixa mista", "a-cx", "abcx", false},
		{"escape", `\n\t`, "\n\t", false},
		{"hífen escapado", `a\-c`, "a-c", false},
		{"hífen final", "a-", "a-", false},
		{"classe", "[:digit:]", "0123456789", false},
		{"colchete literal", "[a", "[a", false},
		{"faixa invertida", "z-a", "", true},
		{"escape incompleto", `a\`, "", true},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			got, err := Expandir(c.in)
			if (err != nil) != c.wantErr || string(got) != c.want {
				t.Fatalf("got %q, %v; want %q (erro=%v)", string(got), err, c.want, c.wantErr)
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
		{"minúsculas para maiúsculas", []string{"a-z", "A-Z"}, "olá mundo", "OLá MUNDO", false},
		{"classe", []string{"[:lower:]", "[:upper:]"}, "abc", "ABC", false},
		{"conj2 menor repete último", []string{"abc", "x"}, "abcd", "xxxd", false},
		{"deletar", []string{"-d", "aeiou"}, "banana e uva", "bnn  v", false},
		{"comprimir espaços", []string{"-s", " "}, "a   b    c", "a b c", false},
		{"traduzir e comprimir", []string{"-s", "a-z", "*"}, "abc 12", "* 12", false},
		{"deletar e comprimir", []string{"-ds", "x", " "}, "axx  b", "a b", false},
		{"quebra de linha", []string{`\n`, " "}, "a\nb\n", "a b ", false},
		{"entrada vazia", []string{"a", "b"}, "", "", false},
		{"sem operandos", nil, "x", "", true},
		{"falta conj2", []string{"abc"}, "x", "", true},
		{"operandos demais", []string{"a", "b", "c"}, "x", "", true},
		{"-d com dois conjuntos", []string{"-d", "a", "b"}, "x", "", true},
		{"faixa inválida", []string{"z-a", "x"}, "x", "", true},
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
