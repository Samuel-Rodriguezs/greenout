package parser

import (
	"errors"
	"reflect"
	"strings"
	"testing"
)

func TestTokenizar(t *testing.T) {
	casos := []struct {
		nome string
		in   string
		quer []Token
	}{
		{"vazio", "", nil},
		{"so espacos", "  \t \n", nil},
		{"palavras", "SET a b", []Token{{"SET", 0, false}, {"a", 4, false}, {"b", 6, false}}},
		{"espacos extras", "  GET   chave  ", []Token{{"GET", 2, false}, {"chave", 8, false}}},
		{"aspas", `SET k "ola mundo"`, []Token{{"SET", 0, false}, {"k", 4, false}, {"ola mundo", 6, true}}},
		{"aspas vazias", `SET k ""`, []Token{{"SET", 0, false}, {"k", 4, false}, {"", 6, true}}},
		{"escapes", `"a\"b\\c\nd\te\rf"`, []Token{{"a\"b\\c\nd\te\rf", 0, true}}},
		{"unicode", `SET çã "ü ñ"`, []Token{{"SET", 0, false}, {"çã", 4, false}, {"ü ñ", 9, true}}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			got, err := Tokenizar(c.in)
			if err != nil {
				t.Fatal(err)
			}
			if !reflect.DeepEqual(got, c.quer) {
				t.Fatalf("got %+v\nquer %+v", got, c.quer)
			}
		})
	}
}

func TestTokenizarErros(t *testing.T) {
	casos := []struct {
		nome string
		in   string
		pos  int
		msg  string
	}{
		{"aspas abertas", `SET k "abc`, 6, "aspas não fechadas"},
		{"escape no fim", `SET k "abc\`, 10, "escape incompleto"},
		{"escape desconhecido", `"a\qb"`, 2, "escape desconhecido"},
		{"colado depois das aspas", `"a"b`, 3, "esperado espaço"},
		{"aspas no meio", `ab"c"`, 2, "aspas no meio"},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			_, err := Tokenizar(c.in)
			var es *ErroSintaxe
			if !errors.As(err, &es) {
				t.Fatalf("err = %v", err)
			}
			if es.Pos != c.pos || !strings.Contains(es.Msg, c.msg) {
				t.Fatalf("got pos=%d msg=%q, quer pos=%d ~%q", es.Pos, es.Msg, c.pos, c.msg)
			}
		})
	}
}

func TestAnalisarValidos(t *testing.T) {
	casos := []struct {
		in   string
		quer Comando
	}{
		{"SET a b", Comando{Tipo: Set, Chave: "a", Valor: "b"}},
		{"set a b", Comando{Tipo: Set, Chave: "a", Valor: "b"}},
		{`SET "chave com espaço" "valor\ncom quebra"`, Comando{Tipo: Set, Chave: "chave com espaço", Valor: "valor\ncom quebra"}},
		{`SET k ""`, Comando{Tipo: Set, Chave: "k", Valor: ""}},
		{"GET Chave", Comando{Tipo: Get, Chave: "Chave"}},
		{"gEt x", Comando{Tipo: Get, Chave: "x"}},
		{"DEL x", Comando{Tipo: Del, Chave: "x"}},
		{"BEGIN", Comando{Tipo: Begin}},
		{"  commit  ", Comando{Tipo: Commit}},
		{"ROLLBACK", Comando{Tipo: Rollback}},
		{"SCAN", Comando{Tipo: Scan}},
		{"SCAN user:", Comando{Tipo: Scan, Prefixo: "user:"}},
		{"SCAN LIMIT 5", Comando{Tipo: Scan, Limite: 5}},
		{"SCAN user: limit 10", Comando{Tipo: Scan, Prefixo: "user:", Limite: 10}},
		{`SCAN "LIMIT"`, Comando{Tipo: Scan, Prefixo: "LIMIT"}},
		{`SCAN "LIMIT" LIMIT 2`, Comando{Tipo: Scan, Prefixo: "LIMIT", Limite: 2}},
		{`GET "BEGIN"`, Comando{Tipo: Get, Chave: "BEGIN"}},
	}
	for _, c := range casos {
		t.Run(c.in, func(t *testing.T) {
			got, err := Analisar(c.in)
			if err != nil {
				t.Fatal(err)
			}
			if got != c.quer {
				t.Fatalf("got %+v, quer %+v", got, c.quer)
			}
		})
	}
}

func TestAnalisarErros(t *testing.T) {
	casos := []struct {
		in  string
		msg string
	}{
		{"", "vazio"},
		{"   ", "vazio"},
		{"FOO a", "desconhecido"},
		{"SET a", "faltam"},
		{"SET", "faltam"},
		{"SET a b c", "a mais"},
		{"GET", "faltam"},
		{"GET a b", "a mais"},
		{"DEL", "faltam"},
		{"BEGIN agora", "a mais"},
		{"COMMIT x", "a mais"},
		{"ROLLBACK x", "a mais"},
		{"SCAN a b", "esperado LIMIT"},
		{"SCAN LIMIT", "precisa de um número"},
		{"SCAN a LIMIT", "precisa de um número"},
		{"SCAN LIMIT zero", "inteiro positivo"},
		{"SCAN LIMIT 0", "inteiro positivo"},
		{"SCAN LIMIT -3", "inteiro positivo"},
		{"SCAN LIMIT 1 2", "a mais"},
		{`SET a "b`, "aspas"},
	}
	for _, c := range casos {
		t.Run(c.in, func(t *testing.T) {
			_, err := Analisar(c.in)
			var es *ErroSintaxe
			if !errors.As(err, &es) {
				t.Fatalf("err = %v", err)
			}
			if !strings.Contains(es.Msg, c.msg) {
				t.Fatalf("msg = %q, esperava conter %q", es.Msg, c.msg)
			}
		})
	}
}

func TestPosicaoDoErro(t *testing.T) {
	_, err := Analisar("SET a b extra")
	var es *ErroSintaxe
	if !errors.As(err, &es) || es.Pos != 8 {
		t.Fatalf("err = %v", err)
	}
	if !strings.Contains(err.Error(), "posição 8") {
		t.Fatalf("mensagem = %q", err.Error())
	}
}

func TestStringDeTipo(t *testing.T) {
	for tipo, quer := range map[Tipo]string{Set: "SET", Get: "GET", Del: "DEL", Scan: "SCAN", Begin: "BEGIN", Commit: "COMMIT", Rollback: "ROLLBACK", Tipo(99): "?"} {
		if tipo.String() != quer {
			t.Errorf("%d = %q, quer %q", tipo, tipo.String(), quer)
		}
	}
}
