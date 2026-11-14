// Pacote recuperacao converte panics em handlers em respostas 500.
package recuperacao

import (
	"net/http"
)

// Middleware captura panics, chama aoPanico (se não nulo) com o valor recuperado
// e responde 500 sem derrubar o servidor.
func Middleware(aoPanico func(r *http.Request, valor any)) func(http.Handler) http.Handler {
	return func(prox http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			defer func() {
				if v := recover(); v != nil {
					if v == http.ErrAbortHandler {
						panic(v)
					}
					if aoPanico != nil {
						aoPanico(r, v)
					}
					http.Error(w, "erro interno", http.StatusInternalServerError)
				}
			}()
			prox.ServeHTTP(w, r)
		})
	}
}
