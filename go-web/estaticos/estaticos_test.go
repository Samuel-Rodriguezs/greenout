package estaticos

import (
	"net/http/httptest"
	"strings"
	"testing"
	"testing/fstest"
)

func TestHandler(t *testing.T) {
	fsys := fstest.MapFS{
		"app.css":         {Data: []byte("body{}")},
		"js/main.js":      {Data: []byte("console.log(1)")},
		"docs/index.html": {Data: []byte("<h1>docs</h1>")},
		"privado/seg.txt": {Data: []byte("segredo")},
		"index.html":      {Data: []byte("<h1>home</h1>")},
	}
	h := Handler(fsys, "/static", 3600)
	casos := []struct {
		nome, metodo, caminho string
		status                int
		contem                string
	}{
		{"arquivo", "GET", "/static/app.css", 200, "body{}"},
		{"subpasta", "GET", "/static/js/main.js", 200, "console.log"},
		{"raiz com index", "GET", "/static/", 200, "home"},
		{"dir com index", "GET", "/static/docs/", 200, "docs"},
		{"dir sem index", "GET", "/static/privado/", 404, ""},
		{"inexistente", "GET", "/static/nada.txt", 404, ""},
		{"fora do prefixo", "GET", "/outro/app.css", 404, ""},
		{"traversal", "GET", "/static/../app.css", 404, ""},
		{"POST", "POST", "/static/app.css", 405, ""},
		{"HEAD", "HEAD", "/static/app.css", 200, ""},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			rec := httptest.NewRecorder()
			h.ServeHTTP(rec, httptest.NewRequest(c.metodo, c.caminho, nil))
			if rec.Code != c.status {
				t.Fatalf("status %d, esperado %d", rec.Code, c.status)
			}
			if !strings.Contains(rec.Body.String(), c.contem) {
				t.Errorf("corpo %q sem %q", rec.Body, c.contem)
			}
			if c.status == 200 && rec.Header().Get("Cache-Control") != "public, max-age=3600" {
				t.Errorf("Cache-Control %q", rec.Header().Get("Cache-Control"))
			}
		})
	}
}

func TestSemCache(t *testing.T) {
	h := Handler(fstest.MapFS{"a.txt": {Data: []byte("x")}}, "/", 0)
	rec := httptest.NewRecorder()
	h.ServeHTTP(rec, httptest.NewRequest("GET", "/a.txt", nil))
	if rec.Code != 200 || rec.Header().Get("Cache-Control") != "" {
		t.Errorf("status %d cache %q", rec.Code, rec.Header().Get("Cache-Control"))
	}
}
