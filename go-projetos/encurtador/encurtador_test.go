package encurtador

import (
	"errors"
	"testing"
)

func TestCodificarDecodificar(t *testing.T) {
	casos := []struct {
		n uint64
		s string
	}{
		{0, "0"}, {9, "9"}, {10, "a"}, {61, "Z"}, {62, "10"}, {3844, "100"},
	}
	for _, c := range casos {
		if got := Codificar(c.n); got != c.s {
			t.Errorf("Codificar(%d) = %q, esperado %q", c.n, got, c.s)
		}
		n, err := Decodificar(c.s)
		if err != nil || n != c.n {
			t.Errorf("Decodificar(%q) = %d, %v", c.s, n, err)
		}
	}
}

func TestDecodificarErros(t *testing.T) {
	for _, s := range []string{"", "ab-c", "é"} {
		if _, err := Decodificar(s); !errors.Is(err, ErrCodigoInvalido) {
			t.Errorf("Decodificar(%q): erro = %v", s, err)
		}
	}
}

func TestEncurtarResolver(t *testing.T) {
	e := Novo()
	c1, err := e.Encurtar("https://exemplo.com/a")
	if err != nil {
		t.Fatal(err)
	}
	c2, _ := e.Encurtar("https://exemplo.com/b")
	c1b, _ := e.Encurtar("https://exemplo.com/a")
	if c1 != c1b || c1 == c2 {
		t.Errorf("códigos inconsistentes: %q %q %q", c1, c1b, c2)
	}
	u, err := e.Resolver(c2)
	if err != nil || u != "https://exemplo.com/b" {
		t.Errorf("Resolver = %q, %v", u, err)
	}
}

func TestEncurtadorErros(t *testing.T) {
	e := Novo()
	for _, u := range []string{"", "ftp://x.com", "sem-esquema.com", "http://"} {
		if _, err := e.Encurtar(u); !errors.Is(err, ErrURLInvalida) {
			t.Errorf("Encurtar(%q): erro = %v", u, err)
		}
	}
	if _, err := e.Resolver("zzz"); !errors.Is(err, ErrNaoEncontrado) {
		t.Errorf("erro = %v", err)
	}
	if _, err := e.Resolver("!"); !errors.Is(err, ErrCodigoInvalido) {
		t.Errorf("erro = %v", err)
	}
}
