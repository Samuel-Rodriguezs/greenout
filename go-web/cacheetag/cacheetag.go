// Pacote cacheetag adiciona ETag às respostas GET e responde 304 quando o
// cliente já possui a versão atual (If-None-Match).
package cacheetag

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"net/http"
	"strings"
)

type buffer struct {
	header http.Header
	status int
	corpo  bytes.Buffer
}

func (b *buffer) Header() http.Header         { return b.header }
func (b *buffer) WriteHeader(c int)           { b.status = c }
func (b *buffer) Write(p []byte) (int, error) { return b.corpo.Write(p) }

// Calcular devolve o ETag forte do conteúdo.
func Calcular(corpo []byte) string {
	h := sha256.Sum256(corpo)
	return `"` + hex.EncodeToString(h[:8]) + `"`
}

func combina(inm, etag string) bool {
	for _, p := range strings.Split(inm, ",") {
		p = strings.TrimPrefix(strings.TrimSpace(p), "W/")
		if p == "*" || p == etag {
			return true
		}
	}
	return false
}

// Middleware só atua em GET/HEAD com resposta 200.
func Middleware(prox http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet && r.Method != http.MethodHead {
			prox.ServeHTTP(w, r)
			return
		}
		buf := &buffer{header: http.Header{}, status: http.StatusOK}
		prox.ServeHTTP(buf, r)
		for k, v := range buf.header {
			w.Header()[k] = v
		}
		if buf.status == http.StatusOK {
			etag := Calcular(buf.corpo.Bytes())
			w.Header().Set("ETag", etag)
			w.Header().Set("Cache-Control", "no-cache")
			if inm := r.Header.Get("If-None-Match"); inm != "" && combina(inm, etag) {
				w.WriteHeader(http.StatusNotModified)
				return
			}
		}
		w.WriteHeader(buf.status)
		w.Write(buf.corpo.Bytes())
	})
}
