package seq

import (
	"bytes"
	"reflect"
	"strings"
	"testing"
)

func TestSequencia(t *testing.T) {
	casos := []struct {
		nome            string
		ini, passo, fim float64
		casas           int
		want            []string
		wantErr         bool
	}{
		{"crescente", 1, 1, 3, 0, []string{"1", "2", "3"}, false},
		{"passo 2", 1, 2, 6, 0, []string{"1", "3", "5"}, false},
		{"decrescente", 3, -1, 1, 0, []string{"3", "2", "1"}, false},
		{"decimal", 0, 0.1, 0.3, 1, []string{"0.0", "0.1", "0.2", "0.3"}, false},
		{"direção errada", 5, 1, 1, 0, []string{}, false},
		{"um elemento", 4, 1, 4, 0, []string{"4"}, false},
		{"negativos", -2, 1, 0, 0, []string{"-2", "-1", "0"}, false},
		{"passo zero", 1, 0, 5, 0, nil, true},
		{"grande demais", 1, 1, 1e9, 0, nil, true},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			got, err := Sequencia(c.ini, c.passo, c.fim, c.casas)
			if (err != nil) != c.wantErr || !reflect.DeepEqual(got, c.want) {
				t.Fatalf("got %v, %v; want %v (erro=%v)", got, err, c.want, c.wantErr)
			}
		})
	}
}

func TestExecutar(t *testing.T) {
	casos := []struct {
		nome    string
		args    []string
		want    string
		wantErr bool
	}{
		{"só fim", []string{"3"}, "1\n2\n3\n", false},
		{"início e fim", []string{"2", "4"}, "2\n3\n4\n", false},
		{"início passo fim", []string{"10", "-5", "0"}, "10\n5\n0\n", false},
		{"separador", []string{"-s", ",", "3"}, "1,2,3\n", false},
		{"igualar largura", []string{"-w", "8", "10"}, "08\n09\n10\n", false},
		{"decimais", []string{"1", "0.5", "2"}, "1.0\n1.5\n2.0\n", false},
		{"vazia", []string{"5", "1"}, "", false},
		{"sem argumentos", nil, "", true},
		{"argumentos demais", []string{"1", "2", "3", "4"}, "", true},
		{"não numérico", []string{"abc"}, "", true},
		{"nan", []string{"NaN"}, "", true},
		{"passo zero", []string{"1", "0", "3"}, "", true},
		{"-s sem valor", []string{"-s"}, "", true},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			var out bytes.Buffer
			err := Executar(c.args, strings.NewReader(""), &out)
			if (err != nil) != c.wantErr || out.String() != c.want {
				t.Fatalf("got %q, %v; want %q (erro=%v)", out.String(), err, c.want, c.wantErr)
			}
		})
	}
}
