package cors

import (
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestMiddleware(t *testing.T) {
	casos := []struct {
		nome       string
		cfg        Config
		metodo     string
		origem     string
		preflight  bool
		status     int
		allowOrig  string
		chamouProx bool
	}{
		{"sem origem", Config{Origens: []string{"*"}}, "GET", "", false, 200, "", true},
		{"curinga", Config{Origens: []string{"*"}}, "GET", "http://x.com", false, 200, "*", true},
		{"origem permitida", Config{Origens: []string{"http://a.com"}}, "GET", "http://a.com", false, 200, "http://a.com", true},
		{"origem negada", Config{Origens: []string{"http://a.com"}}, "GET", "http://b.com", false, 200, "", true},
		{"preflight", Config{Origens: []string{"*"}, Metodos: []string{"GET", "POST"}, Cabecalhos: []string{"Content-Type"}, MaxAgeSegundos: 600}, "OPTIONS", "http://x.com", true, 204, "*", false},
		{"credenciais refletem origem", Config{Origens: []string{"*"}, Credenciais: true}, "GET", "http://x.com", false, 200, "http://x.com", true},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			chamou := false
			h := Middleware(c.cfg)(http.HandlerFunc(func(http.ResponseWriter, *http.Request) { chamou = true }))
			req := httptest.NewRequest(c.metodo, "/", nil)
			if c.origem != "" {
				req.Header.Set("Origin", c.origem)
			}
			if c.preflight {
				req.Header.Set("Access-Control-Request-Method", "POST")
			}
			rec := httptest.NewRecorder()
			h.ServeHTTP(rec, req)
			if rec.Code != c.status {
				t.Errorf("status %d, esperado %d", rec.Code, c.status)
			}
			if got := rec.Header().Get("Access-Control-Allow-Origin"); got != c.allowOrig {
				t.Errorf("Allow-Origin %q, esperado %q", got, c.allowOrig)
			}
			if chamou != c.chamouProx {
				t.Errorf("chamou próximo = %v, esperado %v", chamou, c.chamouProx)
			}
			if c.preflight && (rec.Header().Get("Access-Control-Allow-Methods") != "GET, POST" || rec.Header().Get("Access-Control-Max-Age") != "600") {
				t.Errorf("headers de preflight incorretos: %v", rec.Header())
			}
		})
	}
}
