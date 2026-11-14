// Pacote requestid atribui um identificador único a cada requisição.
package requestid

import (
	"context"
	"crypto/rand"
	"encoding/hex"
	"net/http"
)

// Cabecalho é o nome do header usado para propagar o ID.
const Cabecalho = "X-Request-ID"

type chave struct{}

// Gerar produz um ID aleatório de 16 bytes em hexadecimal.
func Gerar() string {
	b := make([]byte, 16)
	rand.Read(b)
	return hex.EncodeToString(b)
}

// Middleware reaproveita o ID recebido (se houver) ou gera um novo, coloca no
// contexto e devolve no header da resposta. gerar pode ser injetado em testes.
func Middleware(gerar func() string) func(http.Handler) http.Handler {
	if gerar == nil {
		gerar = Gerar
	}
	return func(prox http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			id := r.Header.Get(Cabecalho)
			if id == "" {
				id = gerar()
			}
			w.Header().Set(Cabecalho, id)
			prox.ServeHTTP(w, r.WithContext(context.WithValue(r.Context(), chave{}, id)))
		})
	}
}

// ID extrai o identificador do contexto.
func ID(ctx context.Context) string {
	s, _ := ctx.Value(chave{}).(string)
	return s
}
