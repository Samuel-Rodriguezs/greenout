// Pacote autenticacao oferece middlewares de autenticação Basic e Bearer.
package autenticacao

import (
	"context"
	"crypto/subtle"
	"net/http"
	"strings"
)

type chaveUsuario struct{}

// Usuario extrai do contexto o usuário autenticado.
func Usuario(ctx context.Context) string {
	s, _ := ctx.Value(chaveUsuario{}).(string)
	return s
}

func negar(w http.ResponseWriter, desafio string) {
	w.Header().Set("WWW-Authenticate", desafio)
	http.Error(w, "não autorizado", http.StatusUnauthorized)
}

// Basic exige credenciais HTTP Basic. credenciais mapeia usuário -> senha.
func Basic(dominio string, credenciais map[string]string) func(http.Handler) http.Handler {
	desafio := `Basic realm="` + dominio + `"`
	return func(prox http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			u, s, ok := r.BasicAuth()
			esperada, existe := credenciais[u]
			if !ok || !existe || subtle.ConstantTimeCompare([]byte(s), []byte(esperada)) != 1 {
				negar(w, desafio)
				return
			}
			prox.ServeHTTP(w, r.WithContext(context.WithValue(r.Context(), chaveUsuario{}, u)))
		})
	}
}

// Bearer exige "Authorization: Bearer <token>". validar devolve o usuário dono
// do token e se ele é válido.
func Bearer(validar func(token string) (string, bool)) func(http.Handler) http.Handler {
	return func(prox http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			cab := r.Header.Get("Authorization")
			token, ok := strings.CutPrefix(cab, "Bearer ")
			if !ok || token == "" {
				negar(w, "Bearer")
				return
			}
			usuario, valido := validar(token)
			if !valido {
				negar(w, `Bearer error="invalid_token"`)
				return
			}
			prox.ServeHTTP(w, r.WithContext(context.WithValue(r.Context(), chaveUsuario{}, usuario)))
		})
	}
}
