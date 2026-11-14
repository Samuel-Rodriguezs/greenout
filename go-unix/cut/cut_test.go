package cut

import (
	"bytes"
	"reflect"
	"strings"
	"testing"
)

func TestParseLista(t *testing.T) {
	casos := []struct {
		nome    string
		in      string
		want    []Faixa
		wantErr bool
	}{
		{"simples", "2", []Faixa{{2, 2}}, false},
		{"lista e faixa", "5,1-3", []Faixa{{1, 3}, {5, 5}}, false},
		{"aberta no fim", "4-", []Faixa{{4, 0}}, false},
		{"aberta no início", "-2", []Faixa{{1, 2}}, false},
		{"vazia", "", nil, true},
		{"zero", "0", nil, true},
		{"texto", "a", nil, true},
		{"decrescente", "5-2", nil, true},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			got, err := ParseLista(c.in)
			if (err != nil) != c.wantErr || !reflect.DeepEqual(got, c.want) {
				t.Fatalf("got %v, %v; want %v (erro=%v)", got, err, c.want, c.wantErr)
			}
		})
	}
}

func TestCampos(t *testing.T) {
	casos := []struct {
		nome    string
		linha   string
		lista   string
		somente bool
		want    string
		wantOK  bool
	}{
		{"campo 2", "a:b:c", "2", false, "b", true},
		{"vários", "a:b:c:d", "1,3-", false, "a:c:d", true},
		{"fora do alcance", "a:b", "5", false, "", true},
		{"sem delimitador", "abc", "1", false, "abc", true},
		{"sem delimitador com -s", "abc", "1", true, "abc", false},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			fs, _ := ParseLista(c.lista)
			got, ok := Campos(c.linha, ":", fs, c.somente)
			if got != c.want || ok != c.wantOK {
				t.Fatalf("got %q,%v; want %q,%v", got, ok, c.want, c.wantOK)
			}
		})
	}
}

func TestCaracteres(t *testing.T) {
	fs, _ := ParseLista("2-3,5")
	if got := Caracteres("ação!x", fs); got != "çã!" {
		t.Fatalf("got %q", got)
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
		{"campos csv", []string{"-d", ",", "-f", "2"}, "a,b,c\n1,2,3\n", "b\n2\n", false},
		{"colado", []string{"-d,", "-f1,3"}, "a,b,c\n", "a,c\n", false},
		{"tab padrão", []string{"-f", "2"}, "a\tb\n", "b\n", false},
		{"-s descarta", []string{"-d", ":", "-f", "1", "-s"}, "x\na:b\n", "a\n", false},
		{"caracteres", []string{"-c", "1-2"}, "abc\ndef\n", "ab\nde\n", false},
		{"vazio", []string{"-f", "1"}, "", "", false},
		{"sem modo", []string{"-d", ","}, "a\n", "", true},
		{"delim longo", []string{"-d", "ab", "-f", "1"}, "a\n", "", true},
		{"lista inválida", []string{"-f", "x"}, "a\n", "", true},
		{"-f sem valor", []string{"-f"}, "a\n", "", true},
		{"opção desconhecida", []string{"-z"}, "a\n", "", true},
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
