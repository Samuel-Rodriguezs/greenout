package erros

import (
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestAdaptar(t *testing.T) {
	casos := []struct {
		nome    string
		erro    error
		status  int
		detalhe string
	}{
		{"sem erro", nil, 200, ""},
		{"problema", Novo(404, "usuário 7 não existe"), 404, "usuário 7 não existe"},
		{"problema embrulhado", fmt.Errorf("camada: %w", Novo(422, "campo inválido")), 422, "campo inválido"},
		{"erro genérico", errors.New("senha do banco: abc"), 500, "erro interno"},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			h := Adaptar(func(w http.ResponseWriter, _ *http.Request) error { return c.erro })
			rec := httptest.NewRecorder()
			h.ServeHTTP(rec, httptest.NewRequest("GET", "/x/1", nil))
			if rec.Code != c.status {
				t.Fatalf("status %d, esperado %d", rec.Code, c.status)
			}
			if c.erro == nil {
				return
			}
			if ct := rec.Header().Get("Content-Type"); ct != "application/problem+json" {
				t.Errorf("Content-Type %q", ct)
			}
			var p Problema
			if err := json.Unmarshal(rec.Body.Bytes(), &p); err != nil {
				t.Fatal(err)
			}
			if p.Detalhe != c.detalhe || p.Status != c.status || p.Instancia != "/x/1" || p.Titulo != http.StatusText(c.status) {
				t.Errorf("problema inesperado: %+v", p)
			}
		})
	}
}
