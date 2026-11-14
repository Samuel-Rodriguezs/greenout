package limitador

import (
	"net/http"
	"net/http/httptest"
	"testing"
	"time"
)

func TestMiddleware(t *testing.T) {
	agora := time.Unix(1000, 0)
	l := Novo(2, 10*time.Second, func() time.Time { return agora })
	h := l.Middleware(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {}))

	passos := []struct {
		nome   string
		ip     string
		avanca time.Duration
		status int
		retry  string
	}{
		{"1ª", "1.1.1.1:100", 0, 200, ""},
		{"2ª", "1.1.1.1:101", 3 * time.Second, 200, ""},
		{"3ª excede", "1.1.1.1:102", 0, 429, "7"},
		{"outro IP livre", "2.2.2.2:1", 0, 200, ""},
		{"após janela", "1.1.1.1:103", 8 * time.Second, 200, ""},
	}
	for _, p := range passos {
		t.Run(p.nome, func(t *testing.T) {
			agora = agora.Add(p.avanca)
			req := httptest.NewRequest("GET", "/", nil)
			req.RemoteAddr = p.ip
			rec := httptest.NewRecorder()
			h.ServeHTTP(rec, req)
			if rec.Code != p.status {
				t.Fatalf("status %d, esperado %d", rec.Code, p.status)
			}
			if got := rec.Header().Get("Retry-After"); got != p.retry {
				t.Errorf("Retry-After %q, esperado %q", got, p.retry)
			}
		})
	}
}

func TestPermitirRestantes(t *testing.T) {
	l := Novo(3, time.Minute, func() time.Time { return time.Unix(0, 0) })
	for i, esperado := range []int{2, 1, 0} {
		ok, restam, _ := l.Permitir("x")
		if !ok || restam != esperado {
			t.Errorf("chamada %d: ok=%v restam=%d, esperado %d", i, ok, restam, esperado)
		}
	}
	if ok, _, _ := l.Permitir("x"); ok {
		t.Error("quarta chamada deveria ser negada")
	}
}
