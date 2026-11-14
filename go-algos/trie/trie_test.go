package trie

import (
	"reflect"
	"testing"
)

func montada() *Trie {
	t := Nova()
	for _, p := range []string{"casa", "caso", "casaco", "cama", "carro", "são", "sao"} {
		t.Inserir(p)
	}
	return t
}

func TestInserirContem(t *testing.T) {
	tr := montada()
	if tr.Tamanho() != 7 {
		t.Errorf("tamanho=%d", tr.Tamanho())
	}
	if tr.Inserir("casa") {
		t.Error("reinserção deveria devolver false")
	}
	casos := []struct {
		p    string
		want bool
	}{
		{"casa", true}, {"cas", false}, {"casaco", true}, {"", false}, {"são", true}, {"x", false},
	}
	for _, c := range casos {
		if got := tr.Contem(c.p); got != c.want {
			t.Errorf("Contem(%q)=%v", c.p, got)
		}
	}
	if !tr.TemPrefixo("") || !tr.TemPrefixo("ca") || tr.TemPrefixo("z") {
		t.Error("TemPrefixo inconsistente")
	}
}

func TestComPrefixo(t *testing.T) {
	tr := montada()
	casos := []struct {
		pref string
		want []string
	}{
		{"cas", []string{"casa", "casaco", "caso"}},
		{"ca", []string{"cama", "carro", "casa", "casaco", "caso"}},
		{"z", nil},
		{"carro", []string{"carro"}},
		{"sã", []string{"são"}},
	}
	for _, c := range casos {
		if got := tr.ComPrefixo(c.pref); !reflect.DeepEqual(got, c.want) {
			t.Errorf("ComPrefixo(%q)=%v, esperado %v", c.pref, got, c.want)
		}
	}
	if got := tr.ComPrefixo(""); len(got) != 7 {
		t.Errorf("prefixo vazio devolveu %d palavras", len(got))
	}
}

func TestRemover(t *testing.T) {
	tr := montada()
	if tr.Remover("xyz") {
		t.Error("remover inexistente deveria devolver false")
	}
	if tr.Remover("cas") {
		t.Error("remover prefixo que não é palavra deveria devolver false")
	}
	if !tr.Remover("casaco") || tr.Contem("casaco") || !tr.Contem("casa") {
		t.Error("remoção de casaco incorreta")
	}
	if !tr.Remover("carro") || tr.TemPrefixo("carr") {
		t.Error("ramo de carro deveria ter sido podado")
	}
	if tr.Tamanho() != 5 {
		t.Errorf("tamanho=%d", tr.Tamanho())
	}
}
