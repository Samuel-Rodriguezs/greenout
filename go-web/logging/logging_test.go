package logging

import (
	"bytes"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"
)

func TestMiddleware(t *testing.T) {
	casos := []struct {
		nome, metodo, caminho string
		status                int
		corpo                 string
		esperado              string
	}{
		{"ok implícito", "GET", "/a", 0, "olá", "GET /a 200 4B 1s\n"},
		{"criado", "POST", "/b", 201, "", "POST /b 201 0B 1s\n"},
		{"erro", "GET", "/c", 500, "x", "GET /c 500 1B 1s\n"},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			var buf bytes.Buffer
			t0 := time.Unix(0, 0)
			chamadas := 0
			relogio := func() time.Time {
				chamadas++
				if chamadas == 1 {
					return t0
				}
				return t0.Add(time.Second)
			}
			h := Middleware(&buf, relogio)(http.HandlerFunc(func(w http.ResponseWriter, _ *http.Request) {
				if c.status != 0 {
					w.WriteHeader(c.status)
				}
				w.Write([]byte(c.corpo))
			}))
			h.ServeHTTP(httptest.NewRecorder(), httptest.NewRequest(c.metodo, c.caminho, nil))
			if buf.String() != c.esperado {
				t.Errorf("log %q, esperado %q", buf.String(), c.esperado)
			}
		})
	}
}
