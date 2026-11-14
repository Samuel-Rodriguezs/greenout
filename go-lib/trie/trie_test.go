package trie

import (
	"slices"
	"testing"
)

func montar(chaves ...string) *Trie[int] {
	t := Nova[int]()
	for i, c := range chaves {
		t.Inserir(c, i)
	}
	return t
}

func TestInserirBuscar(t *testing.T) {
	tr := montar("casa", "caso", "ca", "")
	if tr.Tamanho() != 4 {
		t.Fatalf("tamanho %d", tr.Tamanho())
	}
	casos := []struct {
		chave string
		ok    bool
		v     int
	}{
		{"casa", true, 0}, {"caso", true, 1}, {"ca", true, 2}, {"", true, 3},
		{"c", false, 0}, {"casas", false, 0}, {"xyz", false, 0},
	}
	for _, c := range casos {
		v, ok := tr.Buscar(c.chave)
		if ok != c.ok || (ok && v != c.v) {
			t.Errorf("Buscar(%q)=%d,%v", c.chave, v, ok)
		}
	}
	if tr.Inserir("casa", 99) {
		t.Fatal("reinserção não é nova")
	}
	if v, _ := tr.Buscar("casa"); v != 99 || tr.Tamanho() != 4 {
		t.Fatal("reinserção deve sobrescrever sem aumentar tamanho")
	}
}

func TestComPrefixo(t *testing.T) {
	tr := montar("casa", "caso", "carro", "cão", "bola", "ca")
	casos := []struct {
		prefixo string
		want    []string
	}{
		{"ca", []string{"ca", "carro", "casa", "caso"}}, // "cão" tem ã, não a
		{"cas", []string{"casa", "caso"}},
		{"casa", []string{"casa"}},
		{"b", []string{"bola"}},
		{"x", []string{}},
		{"cão", []string{"cão"}},
		{"", []string{"bola", "ca", "carro", "casa", "caso", "cão"}},
	}
	for _, c := range casos {
		t.Run("prefixo "+c.prefixo, func(t *testing.T) {
			if got := tr.ComPrefixo(c.prefixo); !slices.Equal(got, c.want) {
				t.Fatalf("got %v", got)
			}
		})
	}
	if !tr.TemPrefixo("ca") || tr.TemPrefixo("z") {
		t.Fatal("TemPrefixo")
	}
}

func TestRemover(t *testing.T) {
	casos := []struct {
		nome   string
		rem    string
		ok     bool
		resta  []string
		tamNos int // nós sob a raiz após a remoção
	}{
		{"folha poda ramo", "casa", true, []string{"ca", "caso"}, 4},
		{"intermediaria mantem filhos", "ca", true, []string{"casa", "caso"}, 5},
		{"inexistente", "cas", false, []string{"ca", "casa", "caso"}, 5},
		{"fora da trie", "xyz", false, []string{"ca", "casa", "caso"}, 5},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			tr := montar("casa", "caso", "ca")
			if got := tr.Remover(c.rem); got != c.ok {
				t.Fatalf("Remover=%v", got)
			}
			if got := tr.ComPrefixo(""); !slices.Equal(got, c.resta) || tr.Tamanho() != len(c.resta) {
				t.Fatalf("restantes %v tam %d", got, tr.Tamanho())
			}
			if n := contarNos(tr.raiz) - 1; n != c.tamNos {
				t.Fatalf("nós=%d want %d (poda incorreta)", n, c.tamNos)
			}
		})
	}
}

func TestRemoverTudoPodaTudo(t *testing.T) {
	tr := montar("a", "ab", "abc", "b")
	for _, k := range []string{"abc", "ab", "a", "b"} {
		if !tr.Remover(k) {
			t.Fatalf("remover %q", k)
		}
	}
	if tr.Tamanho() != 0 || len(tr.raiz.filhos) != 0 {
		t.Fatal("trie deveria estar vazia")
	}
	if tr.Remover("") {
		t.Fatal("chave vazia não existe")
	}
}

func contarNos[V any](n *no[V]) int {
	c := 1
	for _, f := range n.filhos {
		c += contarNos(f)
	}
	return c
}
