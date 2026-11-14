package tee

import (
	"bytes"
	"errors"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

type escritorQuebrado struct{}

func (escritorQuebrado) Write([]byte) (int, error) { return 0, errors.New("falha de escrita") }

func TestDuplicar(t *testing.T) {
	var a, b bytes.Buffer
	n, err := Duplicar(strings.NewReader("abc"), &a, &b)
	if err != nil || n != 3 || a.String() != "abc" || b.String() != "abc" {
		t.Fatalf("n=%d err=%v a=%q b=%q", n, err, a.String(), b.String())
	}
}

func TestDuplicarSemExtras(t *testing.T) {
	var a bytes.Buffer
	if _, err := Duplicar(strings.NewReader("x"), &a); err != nil || a.String() != "x" {
		t.Fatalf("got %q, %v", a.String(), err)
	}
}

func TestDuplicarErroDeEscrita(t *testing.T) {
	var a bytes.Buffer
	if _, err := Duplicar(strings.NewReader("x"), &a, escritorQuebrado{}); err == nil {
		t.Fatal("esperava erro")
	}
}

func TestExecutar(t *testing.T) {
	dir := t.TempDir()
	f1 := filepath.Join(dir, "1.txt")
	f2 := filepath.Join(dir, "2.txt")
	if err := os.WriteFile(f1, []byte("antigo\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	casos := []struct {
		nome    string
		args    []string
		in      string
		wantOut string
		wantF1  string
		wantErr bool
	}{
		{"só saída", nil, "oi\n", "oi\n", "antigo\n", false},
		{"trunca", []string{f1}, "novo\n", "novo\n", "novo\n", false},
		{"anexa", []string{"-a", f1}, "mais\n", "mais\n", "novo\nmais\n", false},
		{"dois arquivos", []string{f1, f2}, "x\n", "x\n", "x\n", false},
		{"opção inválida", []string{"-z"}, "", "", "x\n", true},
		{"diretório inexistente", []string{filepath.Join(dir, "d", "f")}, "y\n", "y\n", "x\n", true},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			var out bytes.Buffer
			err := Executar(c.args, strings.NewReader(c.in), &out)
			if (err != nil) != c.wantErr || out.String() != c.wantOut {
				t.Fatalf("out=%q err=%v; want %q (erro=%v)", out.String(), err, c.wantOut, c.wantErr)
			}
			got, _ := os.ReadFile(f1)
			if string(got) != c.wantF1 {
				t.Fatalf("arquivo = %q, want %q", got, c.wantF1)
			}
		})
	}
	if got, _ := os.ReadFile(f2); string(got) != "x\n" {
		t.Fatalf("2.txt = %q", got)
	}
}
