package paginacao

import (
	"net/http/httptest"
	"net/url"
	"reflect"
	"testing"
)

func TestLer(t *testing.T) {
	casos := []struct {
		nome, query string
		esperado    Params
	}{
		{"padrão", "", Params{1, 10}},
		{"válidos", "page=3&per_page=25", Params{3, 25}},
		{"inválidos", "page=abc&per_page=-1", Params{1, 10}},
		{"zero", "page=0", Params{1, 10}},
		{"limite", "per_page=5000", Params{1, 100}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			q, _ := url.ParseQuery(c.query)
			if got := Ler(q); got != c.esperado {
				t.Errorf("Ler = %+v, esperado %+v", got, c.esperado)
			}
		})
	}
}

func TestFatiar(t *testing.T) {
	itens := []int{1, 2, 3, 4, 5, 6, 7}
	casos := []struct {
		nome     string
		p        Params
		esperado []int
		paginas  int
	}{
		{"primeira", Params{1, 3}, []int{1, 2, 3}, 3},
		{"última parcial", Params{3, 3}, []int{7}, 3},
		{"além do fim", Params{4, 3}, []int{}, 3},
		{"tudo", Params{1, 100}, itens, 1},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			got, m := Fatiar(itens, c.p)
			if !reflect.DeepEqual(got, c.esperado) {
				t.Errorf("itens %v, esperado %v", got, c.esperado)
			}
			if m.Total != 7 || m.TotalPaginas != c.paginas {
				t.Errorf("meta %+v", m)
			}
		})
	}
	if got, m := Fatiar([]string(nil), Params{1, 10}); len(got) != 0 || m.TotalPaginas != 0 {
		t.Errorf("vazio: %v %+v", got, m)
	}
}

func TestLink(t *testing.T) {
	req := httptest.NewRequest("GET", "/itens?page=2&per_page=3&q=x", nil)
	casos := []struct {
		nome   string
		m      Meta
		contem []string
		naoTem []string
	}{
		{"meio", Meta{2, 3, 7, 3}, []string{`rel="first"`, `rel="prev"`, `rel="next"`, `rel="last"`}, nil},
		{"primeira", Meta{1, 3, 7, 3}, []string{`rel="next"`}, []string{`rel="prev"`}},
		{"última", Meta{3, 3, 7, 3}, []string{`rel="prev"`}, []string{`rel="next"`}},
		{"vazio", Meta{1, 3, 0, 0}, nil, []string{"rel"}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			l := Link(req, c.m)
			for _, s := range c.contem {
				if !contem(l, s) {
					t.Errorf("Link %q sem %s", l, s)
				}
			}
			for _, s := range c.naoTem {
				if contem(l, s) {
					t.Errorf("Link %q não deveria ter %s", l, s)
				}
			}
		})
	}
	if l := Link(req, Meta{2, 3, 7, 3}); !contem(l, "q=x") || !contem(l, "page=3") {
		t.Errorf("Link deveria preservar query: %q", l)
	}
}

func contem(s, sub string) bool {
	for i := 0; i+len(sub) <= len(s); i++ {
		if s[i:i+len(sub)] == sub {
			return true
		}
	}
	return false
}
