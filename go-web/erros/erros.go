// Pacote erros padroniza respostas de erro no formato application/problem+json (RFC 7807/9457).
package erros

import (
	"encoding/json"
	"errors"
	"net/http"
)

// Problema representa um problem details.
type Problema struct {
	Tipo      string `json:"type,omitempty"`
	Titulo    string `json:"title"`
	Status    int    `json:"status"`
	Detalhe   string `json:"detail,omitempty"`
	Instancia string `json:"instance,omitempty"`
}

// Error implementa error.
func (p *Problema) Error() string { return p.Titulo + ": " + p.Detalhe }

// Novo cria um Problema usando o texto padrão do status como título.
func Novo(status int, detalhe string) *Problema {
	return &Problema{Tipo: "about:blank", Titulo: http.StatusText(status), Status: status, Detalhe: detalhe}
}

// Escrever serializa o problema na resposta.
func Escrever(w http.ResponseWriter, r *http.Request, p *Problema) {
	p.Instancia = r.URL.Path
	w.Header().Set("Content-Type", "application/problem+json")
	w.WriteHeader(p.Status)
	json.NewEncoder(w).Encode(p)
}

// HandlerComErro é um handler que pode retornar erro.
type HandlerComErro func(w http.ResponseWriter, r *http.Request) error

// Adaptar converte um HandlerComErro em http.Handler. Erros do tipo *Problema
// mantêm seu status; qualquer outro vira 500 sem vazar a mensagem interna.
func Adaptar(h HandlerComErro) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		err := h(w, r)
		if err == nil {
			return
		}
		var p *Problema
		if errors.As(err, &p) {
			Escrever(w, r, p)
			return
		}
		Escrever(w, r, Novo(http.StatusInternalServerError, "erro interno"))
	})
}
