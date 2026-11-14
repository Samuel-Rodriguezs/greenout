package grep

import (
	"bytes"
	"errors"
	"strings"
	"testing"
)

func TestExecutar(t *testing.T) {
	entrada := "Maçã\nbanana\nCereja\nbanana split\n"
	casos := []struct {
		nome      string
		args      []string
		in        string
		want      string
		wantErr   error
		algumErro bool
	}{
		{"simples", []string{"banana"}, entrada, "banana\nbanana split\n", nil, false},
		{"ignorar caixa", []string{"-i", "cereja"}, entrada, "Cereja\n", nil, false},
		{"inverter", []string{"-v", "banana"}, entrada, "Maçã\nCereja\n", nil, false},
		{"numerar", []string{"-n", "split"}, entrada, "4:banana split\n", nil, false},
		{"contar", []string{"-c", "an"}, entrada, "2\n", nil, false},
		{"combinadas", []string{"-vn", "banana"}, entrada, "1:Maçã\n3:Cereja\n", nil, false},
		{"regex", []string{"^b.*a$"}, entrada, "banana\n", nil, false},
		{"literal", []string{"-F", "a.a"}, "a.a\naxa\n", "a.a\n", nil, false},
		{"sem correspondência", []string{"zzz"}, entrada, "", ErrSemCorrespondencia, false},
		{"contar zero", []string{"-c", "zzz"}, entrada, "0\n", ErrSemCorrespondencia, false},
		{"entrada vazia", []string{"x"}, "", "", ErrSemCorrespondencia, false},
		{"sem padrão", nil, entrada, "", nil, true},
		{"regex inválida", []string{"("}, entrada, "", nil, true},
		{"opção inválida", []string{"-z", "a"}, entrada, "", nil, true},
		{"padrão após --", []string{"--", "-x"}, "-x\n", "-x\n", nil, false},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			var out bytes.Buffer
			err := Executar(c.args, strings.NewReader(c.in), &out)
			if c.algumErro && err == nil {
				t.Fatal("esperava erro")
			}
			if !c.algumErro && !errors.Is(err, c.wantErr) {
				t.Fatalf("erro = %v, esperado %v", err, c.wantErr)
			}
			if out.String() != c.want {
				t.Fatalf("got %q, want %q", out.String(), c.want)
			}
		})
	}
}
