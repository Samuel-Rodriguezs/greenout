package saude

import (
	"context"
	"encoding/json"
	"errors"
	"net/http/httptest"
	"reflect"
	"testing"
	"time"
)

func TestHandler(t *testing.T) {
	ok := func(context.Context) error { return nil }
	falha := func(context.Context) error { return errors.New("sem conexão") }
	lento := func(ctx context.Context) error { <-ctx.Done(); return ctx.Err() }
	casos := []struct {
		nome     string
		itens    map[string]Verificacao
		status   int
		detalhes map[string]string
	}{
		{"vazio", nil, 200, map[string]string{}},
		{"tudo ok", map[string]Verificacao{"db": ok, "cache": ok}, 200, map[string]string{"db": "ok", "cache": "ok"}},
		{"uma falha", map[string]Verificacao{"db": falha, "cache": ok}, 503, map[string]string{"db": "sem conexão", "cache": "ok"}},
		{"timeout", map[string]Verificacao{"api": lento}, 503, map[string]string{"api": "timeout"}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			ch := Novo(20 * time.Millisecond)
			for n, v := range c.itens {
				ch.Registrar(n, v)
			}
			rec := httptest.NewRecorder()
			ch.Handler().ServeHTTP(rec, httptest.NewRequest("GET", "/saude", nil))
			if rec.Code != c.status {
				t.Fatalf("status %d, esperado %d", rec.Code, c.status)
			}
			var rel Relatorio
			if err := json.Unmarshal(rec.Body.Bytes(), &rel); err != nil {
				t.Fatal(err)
			}
			if !reflect.DeepEqual(rel.Detalhes, c.detalhes) {
				t.Errorf("detalhes %v, esperado %v", rel.Detalhes, c.detalhes)
			}
		})
	}
}

func TestNomes(t *testing.T) {
	c := Novo(time.Second)
	c.Registrar("b", nil)
	c.Registrar("a", nil)
	if got := c.Nomes(); !reflect.DeepEqual(got, []string{"a", "b"}) {
		t.Errorf("Nomes = %v", got)
	}
}
