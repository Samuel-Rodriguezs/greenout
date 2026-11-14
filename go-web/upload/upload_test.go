package upload

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"mime/multipart"
	"net/http"
	"net/http/httptest"
	"net/textproto"
	"strings"
	"testing"
)

func corpoMultipart(t *testing.T, campo, nome, tipo, conteudo string) (*bytes.Buffer, string) {
	t.Helper()
	var buf bytes.Buffer
	mw := multipart.NewWriter(&buf)
	h := textproto.MIMEHeader{}
	h.Set("Content-Disposition", `form-data; name="`+campo+`"; filename="`+nome+`"`)
	h.Set("Content-Type", tipo)
	p, err := mw.CreatePart(h)
	if err != nil {
		t.Fatal(err)
	}
	p.Write([]byte(conteudo))
	mw.Close()
	return &buf, mw.FormDataContentType()
}

func TestHandler(t *testing.T) {
	casos := []struct {
		nome, campo, arquivo, tipo, conteudo string
		cfg                                  Config
		status                               int
	}{
		{"ok", "arquivo", "nota.txt", "text/plain", "olá", Config{}, 201},
		{"caminho sanitizado", "arquivo", "../../etc/passwd", "text/plain", "x", Config{}, 201},
		{"campo ausente", "outro", "a.txt", "text/plain", "x", Config{}, 400},
		{"tipo recusado", "arquivo", "a.exe", "application/x-msdownload", "x", Config{TiposAceitos: []string{"text/plain"}}, 415},
		{"muito grande", "arquivo", "a.txt", "text/plain", strings.Repeat("x", 5000), Config{MaxBytes: 1000}, 413},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			arm := NovoArmazem()
			corpo, ct := corpoMultipart(t, c.campo, c.arquivo, c.tipo, c.conteudo)
			req := httptest.NewRequest("POST", "/upload", corpo)
			req.Header.Set("Content-Type", ct)
			rec := httptest.NewRecorder()
			arm.Handler(c.cfg).ServeHTTP(rec, req)
			if rec.Code != c.status {
				t.Fatalf("status %d, esperado %d (%s)", rec.Code, c.status, rec.Body)
			}
			if c.status != 201 {
				return
			}
			var f Arquivo
			if err := json.Unmarshal(rec.Body.Bytes(), &f); err != nil {
				t.Fatal(err)
			}
			soma := sha256.Sum256([]byte(c.conteudo))
			if f.Tamanho != len(c.conteudo) || f.SHA256 != hex.EncodeToString(soma[:]) {
				t.Errorf("metadados incorretos: %+v", f)
			}
			if got, ok := arm.Obter(f.Nome); !ok || string(got) != c.conteudo {
				t.Errorf("conteúdo guardado = %q (%v)", got, ok)
			}
			if strings.Contains(f.Nome, "/") {
				t.Errorf("nome não sanitizado: %q", f.Nome)
			}
		})
	}
}

func TestMetodoEFormularioInvalido(t *testing.T) {
	h := NovoArmazem().Handler(Config{})
	rec := httptest.NewRecorder()
	h.ServeHTTP(rec, httptest.NewRequest("GET", "/", nil))
	if rec.Code != http.StatusMethodNotAllowed {
		t.Errorf("GET: status %d", rec.Code)
	}
	req := httptest.NewRequest("POST", "/", strings.NewReader("lixo"))
	req.Header.Set("Content-Type", "text/plain")
	rec = httptest.NewRecorder()
	h.ServeHTTP(rec, req)
	if rec.Code != http.StatusBadRequest {
		t.Errorf("não multipart: status %d", rec.Code)
	}
}
