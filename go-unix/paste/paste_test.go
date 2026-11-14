package paste

import (
	"bytes"
	"os"
	"path/filepath"
	"reflect"
	"strings"
	"testing"
)

func TestColar(t *testing.T) {
	casos := []struct {
		nome    string
		colunas [][]string
		delims  []rune
		want    []string
	}{
		{"duas colunas", [][]string{{"a", "b"}, {"1", "2"}}, nil, []string{"a\t1", "b\t2"}},
		{"colunas desiguais", [][]string{{"a", "b", "c"}, {"1"}}, []rune{','}, []string{"a,1", "b,", "c,"}},
		{"delimitadores cíclicos", [][]string{{"a"}, {"b"}, {"c"}, {"d"}}, []rune{',', ';'}, []string{"a,b;c,d"}},
		{"uma coluna", [][]string{{"x", "y"}}, nil, []string{"x", "y"}},
		{"sem colunas", nil, nil, []string{}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := Colar(c.colunas, c.delims); !reflect.DeepEqual(got, c.want) {
				t.Fatalf("got %q, want %q", got, c.want)
			}
		})
	}
}

func TestSerial(t *testing.T) {
	casos := []struct {
		nome    string
		colunas [][]string
		delims  []rune
		want    []string
	}{
		{"uma coluna", [][]string{{"a", "b", "c"}}, []rune{','}, []string{"a,b,c"}},
		{"duas colunas", [][]string{{"a", "b"}, {"1", "2"}}, nil, []string{"a\tb", "1\t2"}},
		{"cíclico", [][]string{{"a", "b", "c"}}, []rune{'-', '+'}, []string{"a-b+c"}},
		{"coluna vazia", [][]string{{}}, nil, []string{""}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := Serial(c.colunas, c.delims); !reflect.DeepEqual(got, c.want) {
				t.Fatalf("got %q, want %q", got, c.want)
			}
		})
	}
}

func TestExecutar(t *testing.T) {
	dir := t.TempDir()
	f1, f2 := filepath.Join(dir, "1.txt"), filepath.Join(dir, "2.txt")
	if err := os.WriteFile(f1, []byte("a\nb\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(f2, []byte("1\n2\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	casos := []struct {
		nome    string
		args    []string
		in      string
		want    string
		wantErr bool
	}{
		{"dois arquivos", []string{f1, f2}, "", "a\t1\nb\t2\n", false},
		{"delimitador", []string{"-d", ",", f1, f2}, "", "a,1\nb,2\n", false},
		{"delimitador colado", []string{"-d:", f1, f2}, "", "a:1\nb:2\n", false},
		{"serial", []string{"-s", "-d", ",", f1}, "", "a,b\n", false},
		{"stdin e arquivo", []string{"-", f2}, "x\ny\n", "x\t1\ny\t2\n", false},
		{"stdin implícita", nil, "x\ny\n", "x\ny\n", false},
		{"arquivo inexistente", []string{filepath.Join(dir, "nao")}, "", "", true},
		{"-d sem valor", []string{"-d"}, "", "", true},
		{"delimitador vazio", []string{"-d", "", f1}, "", "", true},
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
