package roteador

import (
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestRoteador(t *testing.T) {
	r := Novo()
	r.HandleFunc("GET", "/", func(w http.ResponseWriter, _ *http.Request) { w.Write([]byte("raiz")) })
	r.HandleFunc("GET", "/usuarios/:id", func(w http.ResponseWriter, q *http.Request) {
		w.Write([]byte("u=" + Parametro(q, "id")))
	})
	r.HandleFunc("POST", "/usuarios/:id", func(w http.ResponseWriter, _ *http.Request) { w.WriteHeader(201) })
	r.HandleFunc("GET", "/a/:x/b/:y", func(w http.ResponseWriter, q *http.Request) {
		w.Write([]byte(Parametro(q, "x") + "-" + Parametro(q, "y")))
	})
	casos := []struct {
		nome, metodo, caminho string
		status                int
		corpo, allow          string
	}{
		{"raiz", "GET", "/", 200, "raiz", ""},
		{"parametro", "GET", "/usuarios/42", 200, "u=42", ""},
		{"barra final", "GET", "/usuarios/7/", 200, "u=7", ""},
		{"post", "POST", "/usuarios/1", 201, "", ""},
		{"dois parametros", "GET", "/a/1/b/2", 200, "1-2", ""},
		{"não encontrado", "GET", "/nada", 404, "404 page not found\n", ""},
		{"segmentos a mais", "GET", "/usuarios/1/x", 404, "404 page not found\n", ""},
		{"método não permitido", "DELETE", "/usuarios/1", 405, "método não permitido\n", "GET, POST"},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			rec := httptest.NewRecorder()
			r.ServeHTTP(rec, httptest.NewRequest(c.metodo, c.caminho, nil))
			if rec.Code != c.status {
				t.Fatalf("status %d, esperado %d", rec.Code, c.status)
			}
			if c.corpo != "" && rec.Body.String() != c.corpo {
				t.Errorf("corpo %q, esperado %q", rec.Body.String(), c.corpo)
			}
			if got := rec.Header().Get("Allow"); got != c.allow {
				t.Errorf("Allow %q, esperado %q", got, c.allow)
			}
		})
	}
}
