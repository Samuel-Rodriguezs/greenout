package requestid

import (
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestMiddleware(t *testing.T) {
	casos := []struct {
		nome, entrada, esperado string
	}{
		{"gera novo", "", "gerado-1"},
		{"reaproveita", "abc", "abc"},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			var noCtx string
			h := Middleware(func() string { return "gerado-1" })(http.HandlerFunc(func(_ http.ResponseWriter, r *http.Request) {
				noCtx = ID(r.Context())
			}))
			req := httptest.NewRequest("GET", "/", nil)
			if c.entrada != "" {
				req.Header.Set(Cabecalho, c.entrada)
			}
			rec := httptest.NewRecorder()
			h.ServeHTTP(rec, req)
			if noCtx != c.esperado || rec.Header().Get(Cabecalho) != c.esperado {
				t.Errorf("ctx=%q header=%q, esperado %q", noCtx, rec.Header().Get(Cabecalho), c.esperado)
			}
		})
	}
}

func TestGerarUnico(t *testing.T) {
	a, b := Gerar(), Gerar()
	if a == b || len(a) != 32 {
		t.Errorf("IDs inválidos: %q %q", a, b)
	}
}
