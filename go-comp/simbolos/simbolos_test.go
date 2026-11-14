package simbolos

import (
	"testing"

	"greenout/comp/token"
)

var pos = token.Posicao{Linha: 1, Coluna: 1}

func TestDeclararEResolver(t *testing.T) {
	tb := Nova()
	if _, err := tb.Declarar("x", Variavel, pos); err != nil {
		t.Fatal(err)
	}
	tb.Entrar(false)
	if _, err := tb.Declarar("y", Variavel, pos); err != nil {
		t.Fatal(err)
	}
	casos := []struct {
		nome         string
		quer         bool
		profundidade int
	}{
		{"x", true, 0}, {"y", true, 1}, {"z", false, 0},
	}
	for _, c := range casos {
		s, ok := tb.Resolver(c.nome)
		if ok != c.quer {
			t.Errorf("Resolver(%q) ok = %v, quer %v", c.nome, ok, c.quer)
			continue
		}
		if ok && s.Profundidade != c.profundidade {
			t.Errorf("%q profundidade = %d, quer %d", c.nome, s.Profundidade, c.profundidade)
		}
	}
	if _, ok := tb.ResolverLocal("x"); ok {
		t.Error("x não deveria ser local no bloco interno")
	}
	tb.Sair()
	if _, ok := tb.Resolver("y"); ok {
		t.Error("y não deveria ser visível após Sair")
	}
}

func TestRedeclaracaoESombreamento(t *testing.T) {
	tb := Nova()
	primeiro, _ := tb.Declarar("a", Variavel, token.Posicao{Linha: 1, Coluna: 5})
	ant, err := tb.Declarar("a", Variavel, token.Posicao{Linha: 2, Coluna: 5})
	if err == nil || ant != primeiro {
		t.Fatalf("esperado erro devolvendo o símbolo original, veio %v %v", ant, err)
	}
	tb.Entrar(false)
	interno, err := tb.Declarar("a", Variavel, pos)
	if err != nil {
		t.Fatalf("sombreamento deveria ser permitido: %v", err)
	}
	if s, _ := tb.Resolver("a"); s != interno {
		t.Error("deveria resolver para o símbolo interno")
	}
	tb.Sair()
	if s, _ := tb.Resolver("a"); s != primeiro {
		t.Error("deveria voltar ao símbolo externo")
	}
}

func TestIndicesEOrdem(t *testing.T) {
	tb := Nova()
	for _, n := range []string{"a", "b", "c"} {
		tb.Declarar(n, Variavel, pos)
	}
	for i, s := range tb.Atual().Simbolos() {
		if s.Indice != i {
			t.Errorf("%s indice = %d, quer %d", s.Nome, s.Indice, i)
		}
	}
}

func TestEmbutidosNoUniverso(t *testing.T) {
	tb := Nova()
	tb.DeclararEmbutido("len", "dado")
	s, ok := tb.Resolver("len")
	if !ok || s.Categoria != Embutido || s.Profundidade != -1 || s.Dado != "dado" {
		t.Fatalf("embutido = %+v %v", s, ok)
	}
	// o usuário pode sombrear um embutido no global
	if _, err := tb.Declarar("len", Variavel, pos); err != nil {
		t.Errorf("sombrear embutido deveria ser permitido: %v", err)
	}
	if s, _ := tb.Resolver("len"); s.Categoria != Variavel {
		t.Error("deveria resolver para a variável do usuário")
	}
}

func TestSairNoGlobalEDentroDeFuncao(t *testing.T) {
	tb := Nova()
	if tb.Sair() != nil {
		t.Error("Sair no global deveria devolver nil")
	}
	if tb.DentroDeFuncao() {
		t.Error("global não está dentro de função")
	}
	tb.Entrar(true)
	tb.Entrar(false)
	if !tb.DentroDeFuncao() || tb.Profundidade() != 2 {
		t.Errorf("dentro=%v prof=%d", tb.DentroDeFuncao(), tb.Profundidade())
	}
	tb.Sair()
	tb.Sair()
	if tb.DentroDeFuncao() || tb.Profundidade() != 0 {
		t.Error("deveria estar de volta ao global")
	}
}

func TestNaoUsados(t *testing.T) {
	tb := Nova()
	tb.Entrar(true)
	tb.Declarar("p", Parametro, pos)
	a, _ := tb.Declarar("a", Variavel, pos)
	b, _ := tb.Declarar("b", Variavel, pos)
	tb.Declarar("f", Funcao, pos)
	a.Usado = true
	esc := tb.Sair()
	nu := esc.NaoUsados()
	if len(nu) != 1 || nu[0] != b {
		t.Errorf("NaoUsados = %v, quer só b", nu)
	}
}

func TestCategoriaString(t *testing.T) {
	casos := map[Categoria]string{Variavel: "variável", Funcao: "função", Parametro: "parâmetro", Embutido: "embutido", Categoria(9): "Categoria(9)"}
	for c, q := range casos {
		if c.String() != q {
			t.Errorf("%d = %q, quer %q", int(c), c.String(), q)
		}
	}
}
