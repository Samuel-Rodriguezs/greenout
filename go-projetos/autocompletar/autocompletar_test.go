package autocompletar

import (
	"reflect"
	"testing"
)

func trieExemplo() *Trie {
	t := Nova()
	t.Inserir("casa", 5)
	t.Inserir("casaco", 2)
	t.Inserir("cama", 8)
	t.Inserir("carro", 8)
	t.Inserir("bola", 1)
	return t
}

func TestSugerir(t *testing.T) {
	casos := []struct {
		nome, prefixo string
		limite        int
		want          []string
	}{
		{"prefixo ca", "ca", 0, []string{"cama", "carro", "casa", "casaco"}},
		{"limite", "ca", 2, []string{"cama", "carro"}},
		{"prefixo exato inclui a própria", "casa", 0, []string{"casa", "casaco"}},
		{"maiúsculas e espaços", "  CAS ", 0, []string{"casa", "casaco"}},
		{"sem resultados", "xyz", 0, nil},
		{"prefixo vazio devolve tudo", "", 0, []string{"cama", "carro", "casa", "casaco", "bola"}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			got := trieExemplo().Sugerir(c.prefixo, c.limite)
			if !reflect.DeepEqual(got, c.want) {
				t.Errorf("got %v, want %v", got, c.want)
			}
		})
	}
}

func TestInserirAcumulaPeso(t *testing.T) {
	tr := trieExemplo()
	tr.Inserir("casaco", 10)
	if got := tr.Sugerir("cas", 1); !reflect.DeepEqual(got, []string{"casaco"}) {
		t.Errorf("got %v", got)
	}
	if tr.Tamanho() != 5 {
		t.Errorf("Tamanho = %d, esperado 5", tr.Tamanho())
	}
}

func TestContemEVazio(t *testing.T) {
	tr := trieExemplo()
	tr.Inserir("   ", 3)
	if tr.Tamanho() != 5 {
		t.Error("palavra vazia não deveria ser inserida")
	}
	if !tr.Contem("CASA") || tr.Contem("cas") || tr.Contem("zebra") {
		t.Error("Contem retornou valor errado")
	}
}

func TestAcentos(t *testing.T) {
	tr := Nova()
	tr.Inserir("ação", 1)
	tr.Inserir("açúcar", 2)
	if got := tr.Sugerir("aç", 0); !reflect.DeepEqual(got, []string{"açúcar", "ação"}) {
		t.Errorf("got %v", got)
	}
}
