package compressao

import (
	"compress/gzip"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
)

func TestMiddleware(t *testing.T) {
	texto := strings.Repeat("olá mundo ", 100)
	h := Middleware(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
		io.WriteString(w, texto)
	}))
	casos := []struct {
		nome, aceita string
		comprimido   bool
	}{
		{"gzip", "gzip", true},
		{"lista", "deflate, gzip;q=0.8", true},
		{"maiúsculas", "GZIP", true},
		{"q=0", "gzip;q=0", false},
		{"nenhum", "", false},
		{"outro", "br", false},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			req := httptest.NewRequest("GET", "/", nil)
			if c.aceita != "" {
				req.Header.Set("Accept-Encoding", c.aceita)
			}
			rec := httptest.NewRecorder()
			h.ServeHTTP(rec, req)
			if rec.Header().Get("Vary") != "Accept-Encoding" {
				t.Error("faltou Vary")
			}
			if c.comprimido {
				if rec.Header().Get("Content-Encoding") != "gzip" {
					t.Fatal("faltou Content-Encoding")
				}
				zr, err := gzip.NewReader(rec.Body)
				if err != nil {
					t.Fatal(err)
				}
				b, _ := io.ReadAll(zr)
				if string(b) != texto {
					t.Error("corpo descomprimido difere")
				}
				if rec.Body.Len() >= len(texto) {
					t.Error("não comprimiu")
				}
			} else {
				if rec.Header().Get("Content-Encoding") != "" || rec.Body.String() != texto {
					t.Error("não deveria comprimir")
				}
			}
		})
	}
}
