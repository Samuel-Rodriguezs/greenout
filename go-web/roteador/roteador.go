// Pacote roteador implementa um roteador HTTP simples com parâmetros de caminho
// no formato /usuarios/:id.
package roteador

import (
	"context"
	"net/http"
	"strings"
)

type chaveParams struct{}

type rota struct {
	metodo    string
	segmentos []string
	handler   http.Handler
}

// Roteador despacha requisições por método e padrão de caminho.
type Roteador struct {
	rotas []rota
	// NaoEncontrado é usado quando nenhum caminho casa.
	NaoEncontrado http.Handler
}

// Novo cria um roteador vazio.
func Novo() *Roteador {
	return &Roteador{NaoEncontrado: http.NotFoundHandler()}
}

func dividir(caminho string) []string {
	caminho = strings.Trim(caminho, "/")
	if caminho == "" {
		return nil
	}
	return strings.Split(caminho, "/")
}

// Handle registra um handler para método e padrão.
func (r *Roteador) Handle(metodo, padrao string, h http.Handler) {
	r.rotas = append(r.rotas, rota{metodo: metodo, segmentos: dividir(padrao), handler: h})
}

// HandleFunc registra uma função como handler.
func (r *Roteador) HandleFunc(metodo, padrao string, f http.HandlerFunc) {
	r.Handle(metodo, padrao, f)
}

// Parametro retorna o valor do parâmetro de caminho nomeado.
func Parametro(req *http.Request, nome string) string {
	m, _ := req.Context().Value(chaveParams{}).(map[string]string)
	return m[nome]
}

func casar(padrao, partes []string) (map[string]string, bool) {
	if len(padrao) != len(partes) {
		return nil, false
	}
	params := map[string]string{}
	for i, p := range padrao {
		if strings.HasPrefix(p, ":") {
			params[p[1:]] = partes[i]
		} else if p != partes[i] {
			return nil, false
		}
	}
	return params, true
}

// ServeHTTP implementa http.Handler. Responde 405 com Allow quando o caminho
// existe mas o método não.
func (r *Roteador) ServeHTTP(w http.ResponseWriter, req *http.Request) {
	partes := dividir(req.URL.Path)
	var permitidos []string
	for _, rt := range r.rotas {
		params, ok := casar(rt.segmentos, partes)
		if !ok {
			continue
		}
		if rt.metodo != req.Method {
			permitidos = append(permitidos, rt.metodo)
			continue
		}
		ctx := context.WithValue(req.Context(), chaveParams{}, params)
		rt.handler.ServeHTTP(w, req.WithContext(ctx))
		return
	}
	if len(permitidos) > 0 {
		w.Header().Set("Allow", strings.Join(permitidos, ", "))
		http.Error(w, "método não permitido", http.StatusMethodNotAllowed)
		return
	}
	r.NaoEncontrado.ServeHTTP(w, req)
}
