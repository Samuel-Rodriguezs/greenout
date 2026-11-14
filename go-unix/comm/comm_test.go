package comm

import (
	"bytes"
	"os"
	"path/filepath"
	"reflect"
	"strings"
	"testing"
)

func TestComparar(t *testing.T) {
	casos := []struct {
		nome string
		a, b []string
		want []Linha
	}{
		{"ambos vazios", nil, nil, nil},
		{"só primeiro", []string{"a"}, nil, []Linha{{1, "a"}}},
		{"só segundo", nil, []string{"a"}, []Linha{{2, "a"}}},
		{"idênticos", []string{"a", "b"}, []string{"a", "b"}, []Linha{{3, "a"}, {3, "b"}}},
		{"misto", []string{"a", "c", "d"}, []string{"b", "c", "e"},
			[]Linha{{1, "a"}, {2, "b"}, {3, "c"}, {1, "d"}, {2, "e"}}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := Comparar(c.a, c.b); !reflect.DeepEqual(got, c.want) {
				t.Fatalf("got %v, want %v", got, c.want)
			}
		})
	}
}

func TestFormatar(t *testing.T) {
	ls := []Linha{{1, "a"}, {2, "b"}, {3, "c"}}
	casos := []struct {
		nome     string
		suprimir [4]bool
		want     []string
	}{
		{"nenhuma", [4]bool{}, []string{"a", "\tb", "\t\tc"}},
		{"sem coluna 1", [4]bool{1: true}, []string{"b", "\tc"}},
		{"sem coluna 3", [4]bool{3: true}, []string{"a", "\tb"}},
		{"só coluna 3", [4]bool{1: true, 2: true}, []string{"c"}},
		{"tudo suprimido", [4]bool{1: true, 2: true, 3: true}, nil},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := Formatar(ls, c.suprimir); !reflect.DeepEqual(got, c.want) {
				t.Fatalf("got %q, want %q", got, c.want)
			}
		})
	}
}

func TestExecutar(t *testing.T) {
	dir := t.TempDir()
	f1, f2 := filepath.Join(dir, "1.txt"), filepath.Join(dir, "2.txt")
	if err := os.WriteFile(f1, []byte("a\nb\nc\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(f2, []byte("b\nc\nd\n"), 0o644); err != nil {
		t.Fatal(err)
	}
	casos := []struct {
		nome    string
		args    []string
		in      string
		want    string
		wantErr bool
	}{
		{"três colunas", []string{f1, f2}, "", "a\n\t\tb\n\t\tc\n\td\n", false},
		{"só comuns", []string{"-12", f1, f2}, "", "b\nc\n", false},
		{"só exclusivas do primeiro", []string{"-23", f1, f2}, "", "a\n", false},
		{"stdin como segundo", []string{"-3", f1, "-"}, "c\nz\n", "a\nb\n\tz\n", false},
		{"arquivo inexistente", []string{f1, filepath.Join(dir, "nao")}, "", "", true},
		{"poucos operandos", []string{f1}, "", "", true},
		{"dois hífens", []string{"-", "-"}, "", "", true},
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
