// Pacote logging fornece um middleware que registra método, caminho, status,
// bytes e duração de cada requisição em um io.Writer injetável.
package logging

import (
	"fmt"
	"io"
	"net/http"
	"time"
)

type gravador struct {
	http.ResponseWriter
	status int
	bytes  int
}

func (g *gravador) WriteHeader(c int) {
	g.status = c
	g.ResponseWriter.WriteHeader(c)
}

func (g *gravador) Write(b []byte) (int, error) {
	n, err := g.ResponseWriter.Write(b)
	g.bytes += n
	return n, err
}

// Middleware retorna um middleware que escreve uma linha por requisição em saida.
// agora é o relógio usado para medir duração (injetável em testes).
func Middleware(saida io.Writer, agora func() time.Time) func(http.Handler) http.Handler {
	if agora == nil {
		agora = time.Now
	}
	return func(prox http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			ini := agora()
			g := &gravador{ResponseWriter: w, status: http.StatusOK}
			prox.ServeHTTP(g, r)
			fmt.Fprintf(saida, "%s %s %d %dB %s\n", r.Method, r.URL.Path, g.status, g.bytes, agora().Sub(ini))
		})
	}
}
