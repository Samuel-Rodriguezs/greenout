// Pacote cors implementa um middleware de Cross-Origin Resource Sharing.
package cors

import (
	"net/http"
	"strconv"
	"strings"
)

// Config define as políticas de CORS.
type Config struct {
	Origens        []string // "*" libera qualquer origem
	Metodos        []string
	Cabecalhos     []string
	Credenciais    bool
	MaxAgeSegundos int
}

func (c Config) permitida(origem string) bool {
	for _, o := range c.Origens {
		if o == "*" || o == origem {
			return true
		}
	}
	return false
}

// Middleware aplica a política. Preflights (OPTIONS com Access-Control-Request-Method)
// são respondidos com 204 sem chamar o próximo handler.
func Middleware(c Config) func(http.Handler) http.Handler {
	return func(prox http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			origem := r.Header.Get("Origin")
			if origem == "" || !c.permitida(origem) {
				prox.ServeHTTP(w, r)
				return
			}
			h := w.Header()
			if len(c.Origens) == 1 && c.Origens[0] == "*" && !c.Credenciais {
				h.Set("Access-Control-Allow-Origin", "*")
			} else {
				h.Set("Access-Control-Allow-Origin", origem)
				h.Add("Vary", "Origin")
			}
			if c.Credenciais {
				h.Set("Access-Control-Allow-Credentials", "true")
			}
			if r.Method == http.MethodOptions && r.Header.Get("Access-Control-Request-Method") != "" {
				h.Set("Access-Control-Allow-Methods", strings.Join(c.Metodos, ", "))
				h.Set("Access-Control-Allow-Headers", strings.Join(c.Cabecalhos, ", "))
				if c.MaxAgeSegundos > 0 {
					h.Set("Access-Control-Max-Age", strconv.Itoa(c.MaxAgeSegundos))
				}
				w.WriteHeader(http.StatusNoContent)
				return
			}
			prox.ServeHTTP(w, r)
		})
	}
}
