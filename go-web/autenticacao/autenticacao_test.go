package autenticacao

import (
	"net/http"
	"net/http/httptest"
	"testing"
)

func eco(w http.ResponseWriter, r *http.Request) { w.Write([]byte(Usuario(r.Context()))) }

func TestBasic(t *testing.T) {
	h := Basic("lab", map[string]string{"ana": "123"})(http.HandlerFunc(eco))
	casos := []struct {
		nome, user, senha string
		semHeader         bool
		status            int
		corpo             string
	}{
		{"válido", "ana", "123", false, 200, "ana"},
		{"senha errada", "ana", "x", false, 401, ""},
		{"usuário inexistente", "bob", "123", false, 401, ""},
		{"sem header", "", "", true, 401, ""},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			req := httptest.NewRequest("GET", "/", nil)
			if !c.semHeader {
				req.SetBasicAuth(c.user, c.senha)
			}
			rec := httptest.NewRecorder()
			h.ServeHTTP(rec, req)
			if rec.Code != c.status {
				t.Fatalf("status %d, esperado %d", rec.Code, c.status)
			}
			if c.status == 200 && rec.Body.String() != c.corpo {
				t.Errorf("corpo %q", rec.Body.String())
			}
			if c.status == 401 && rec.Header().Get("WWW-Authenticate") != `Basic realm="lab"` {
				t.Errorf("WWW-Authenticate %q", rec.Header().Get("WWW-Authenticate"))
			}
		})
	}
}

func TestBearer(t *testing.T) {
	h := Bearer(func(tk string) (string, bool) {
		if tk == "segredo" {
			return "carla", true
		}
		return "", false
	})(http.HandlerFunc(eco))
	casos := []struct {
		nome, cabecalho string
		status          int
	}{
		{"válido", "Bearer segredo", 200},
		{"inválido", "Bearer outro", 401},
		{"sem prefixo", "segredo", 401},
		{"vazio", "", 401},
		{"token vazio", "Bearer ", 401},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			req := httptest.NewRequest("GET", "/", nil)
			if c.cabecalho != "" {
				req.Header.Set("Authorization", c.cabecalho)
			}
			rec := httptest.NewRecorder()
			h.ServeHTTP(rec, req)
			if rec.Code != c.status {
				t.Fatalf("status %d, esperado %d", rec.Code, c.status)
			}
			if c.status == 200 && rec.Body.String() != "carla" {
				t.Errorf("usuário %q", rec.Body.String())
			}
		})
	}
}
