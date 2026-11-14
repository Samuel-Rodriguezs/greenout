package recuperacao

import (
	"errors"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestMiddleware(t *testing.T) {
	casos := []struct {
		nome    string
		handler http.HandlerFunc
		status  int
		panico  string
	}{
		{"sem panic", func(w http.ResponseWriter, _ *http.Request) { w.WriteHeader(204) }, 204, ""},
		{"panic string", func(http.ResponseWriter, *http.Request) { panic("boom") }, 500, "boom"},
		{"panic error", func(http.ResponseWriter, *http.Request) { panic(errors.New("falha")) }, 500, "falha"},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			var visto string
			h := Middleware(func(_ *http.Request, v any) {
				if e, ok := v.(error); ok {
					visto = e.Error()
				} else {
					visto = v.(string)
				}
			})(c.handler)
			rec := httptest.NewRecorder()
			h.ServeHTTP(rec, httptest.NewRequest("GET", "/", nil))
			if rec.Code != c.status {
				t.Errorf("status %d, esperado %d", rec.Code, c.status)
			}
			if visto != c.panico {
				t.Errorf("panic registrado %q, esperado %q", visto, c.panico)
			}
		})
	}
}

func TestAbortHandlerRepropaga(t *testing.T) {
	h := Middleware(nil)(http.HandlerFunc(func(http.ResponseWriter, *http.Request) { panic(http.ErrAbortHandler) }))
	defer func() {
		if recover() != http.ErrAbortHandler {
			t.Error("ErrAbortHandler deveria ser repropagado")
		}
	}()
	h.ServeHTTP(httptest.NewRecorder(), httptest.NewRequest("GET", "/", nil))
}
