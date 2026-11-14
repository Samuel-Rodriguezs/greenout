package cacheetag

import (
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestMiddleware(t *testing.T) {
	h := Middleware(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.URL.Path == "/erro" {
			http.Error(w, "x", 500)
			return
		}
		w.Write([]byte("conteúdo"))
	}))
	etag := Calcular([]byte("conteúdo"))
	casos := []struct {
		nome, metodo, caminho, inm string
		status                     int
		temCorpo, temEtag          bool
	}{
		{"primeira", "GET", "/", "", 200, true, true},
		{"igual", "GET", "/", etag, 304, false, true},
		{"fraco", "GET", "/", "W/" + etag, 304, false, true},
		{"lista", "GET", "/", `"x", ` + etag, 304, false, true},
		{"curinga", "GET", "/", "*", 304, false, true},
		{"diferente", "GET", "/", `"outro"`, 200, true, true},
		{"post ignora", "POST", "/", etag, 200, true, false},
		{"erro sem etag", "GET", "/erro", "", 500, true, false},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			req := httptest.NewRequest(c.metodo, c.caminho, nil)
			if c.inm != "" {
				req.Header.Set("If-None-Match", c.inm)
			}
			rec := httptest.NewRecorder()
			h.ServeHTTP(rec, req)
			if rec.Code != c.status {
				t.Fatalf("status %d, esperado %d", rec.Code, c.status)
			}
			if (rec.Body.Len() > 0) != c.temCorpo {
				t.Errorf("corpo presente = %v", rec.Body.Len() > 0)
			}
			if (rec.Header().Get("ETag") != "") != c.temEtag {
				t.Errorf("ETag = %q", rec.Header().Get("ETag"))
			}
		})
	}
}
