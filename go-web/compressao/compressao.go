// Pacote compressao comprime respostas com gzip quando o cliente aceita.
package compressao

import (
	"compress/gzip"
	"net/http"
	"strings"
)

type gzipWriter struct {
	http.ResponseWriter
	gz *gzip.Writer
}

func (g *gzipWriter) Write(b []byte) (int, error) { return g.gz.Write(b) }

func aceitaGzip(r *http.Request) bool {
	for _, parte := range strings.Split(r.Header.Get("Accept-Encoding"), ",") {
		nome, q, _ := strings.Cut(strings.TrimSpace(parte), ";")
		if strings.EqualFold(strings.TrimSpace(nome), "gzip") && strings.TrimSpace(q) != "q=0" {
			return true
		}
	}
	return false
}

// Middleware comprime o corpo com gzip se o cliente enviar Accept-Encoding: gzip.
func Middleware(prox http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.Header().Add("Vary", "Accept-Encoding")
		if !aceitaGzip(r) {
			prox.ServeHTTP(w, r)
			return
		}
		w.Header().Set("Content-Encoding", "gzip")
		w.Header().Del("Content-Length")
		gz := gzip.NewWriter(w)
		defer gz.Close()
		prox.ServeHTTP(&gzipWriter{ResponseWriter: w, gz: gz}, r)
	})
}
