package argumentos

import (
	"errors"
	"reflect"
	"testing"
)

func novo() (*Parser, *string, *int, *bool) {
	p := &Parser{}
	return p, p.Texto("nome", "n", "padrao"), p.Inteiro("vezes", "v", 1), p.Booleano("verboso", "V")
}

func TestInterpretar(t *testing.T) {
	casos := []struct {
		nome    string
		args    []string
		texto   string
		inteiro int
		bool_   bool
		pos     []string
	}{
		{"padroes", nil, "padrao", 1, false, nil},
		{"igual", []string{"--nome=ana", "--vezes=3"}, "ana", 3, false, nil},
		{"espaco", []string{"--nome", "bia", "-v", "5"}, "bia", 5, false, nil},
		{"booleano", []string{"-V"}, "padrao", 1, true, nil},
		{"booleano explicito falso", []string{"--verboso=false"}, "padrao", 1, false, nil},
		{"posicionais", []string{"a", "-n", "x", "b"}, "x", 1, false, []string{"a", "b"}},
		{"terminador", []string{"-V", "--", "--nome", "c"}, "padrao", 1, true, []string{"--nome", "c"}},
		{"hifen sozinho", []string{"-"}, "padrao", 1, false, []string{"-"}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			p, s, i, b := novo()
			pos, err := p.Interpretar(c.args)
			if err != nil {
				t.Fatal(err)
			}
			if *s != c.texto || *i != c.inteiro || *b != c.bool_ || !reflect.DeepEqual(pos, c.pos) {
				t.Errorf("got %q %d %v %v", *s, *i, *b, pos)
			}
		})
	}
}

func TestInterpretarErros(t *testing.T) {
	casos := []struct {
		nome string
		args []string
		err  error
	}{
		{"desconhecida", []string{"--x"}, ErrDesconhecida},
		{"sem valor", []string{"--nome"}, ErrSemValor},
		{"int invalido", []string{"--vezes=abc"}, ErrValor},
		{"bool invalido", []string{"--verboso=talvez"}, ErrValor},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			p, _, _, _ := novo()
			if _, err := p.Interpretar(c.args); !errors.Is(err, c.err) {
				t.Errorf("erro = %v, esperado %v", err, c.err)
			}
		})
	}
}
