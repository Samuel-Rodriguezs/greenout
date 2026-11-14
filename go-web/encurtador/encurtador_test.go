package encurtador

import (
	"encoding/json"
	"net/http/httptest"
	"strconv"
	"strings"
	"sync"
	"testing"
	"time"
)

func novoTeste() *Servico {
	n := 0
	return Novo(func() time.Time { return time.Unix(1700000000, 0).UTC() }, func() string {
		n++
		return "gen" + strconv.Itoa(n)
	})
}

func TestFluxoHTTP(t *testing.T) {
	h := novoTeste().Handler()
	passos := []struct {
		nome, metodo, caminho, corpo string
		status                       int
		contem, location             string
	}{
		{"cria automático", "POST", "/api/links", `{"url":"https://exemplo.com/a"}`, 201, `"codigo":"gen1"`, "/gen1"},
		{"cria personalizado", "POST", "/api/links", `{"url":"http://x.org","codigo":"meu-link"}`, 201, "meu-link", "/meu-link"},
		{"código em uso", "POST", "/api/links", `{"url":"http://x.org","codigo":"meu-link"}`, 409, "já em uso", ""},
		{"código inválido", "POST", "/api/links", `{"url":"http://x.org","codigo":"a b"}`, 400, "código inválido", ""},
		{"url sem esquema", "POST", "/api/links", `{"url":"exemplo.com"}`, 400, "url inválida", ""},
		{"url ftp", "POST", "/api/links", `{"url":"ftp://x.com/a"}`, 400, "url inválida", ""},
		{"JSON ruim", "POST", "/api/links", `nada`, 400, "JSON inválido", ""},
		{"redireciona", "GET", "/gen1", "", 302, "", "https://exemplo.com/a"},
		{"redireciona 2", "GET", "/gen1", "", 302, "", "https://exemplo.com/a"},
		{"stats", "GET", "/api/links/gen1", "", 200, `"acessos":2`, ""},
		{"stats sem contar", "GET", "/api/links/gen1", "", 200, `"acessos":2`, ""},
		{"não existe", "GET", "/zzz", "", 404, "não encontrado", ""},
		{"stats inexistente", "GET", "/api/links/zzz", "", 404, "não encontrado", ""},
		{"remove", "DELETE", "/api/links/gen1", "", 204, "", ""},
		{"remove de novo", "DELETE", "/api/links/gen1", "", 404, "não encontrado", ""},
		{"após remover", "GET", "/gen1", "", 404, "", ""},
	}
	for _, p := range passos {
		t.Run(p.nome, func(t *testing.T) {
			rec := httptest.NewRecorder()
			h.ServeHTTP(rec, httptest.NewRequest(p.metodo, p.caminho, strings.NewReader(p.corpo)))
			if rec.Code != p.status {
				t.Fatalf("status %d, esperado %d (%s)", rec.Code, p.status, rec.Body)
			}
			if !strings.Contains(rec.Body.String(), p.contem) {
				t.Errorf("corpo %q sem %q", rec.Body, p.contem)
			}
			if got := rec.Header().Get("Location"); got != p.location {
				t.Errorf("Location %q, esperado %q", got, p.location)
			}
		})
	}
}

func TestGeradorColisao(t *testing.T) {
	seq := []string{"a1b", "a1b", "c2d"}
	i := 0
	s := Novo(nil, func() string { v := seq[i]; i++; return v })
	l1, _ := s.Criar("http://x.com", "")
	l2, _ := s.Criar("http://y.com", "")
	if l1.Codigo != "a1b" || l2.Codigo != "c2d" {
		t.Errorf("códigos %q %q", l1.Codigo, l2.Codigo)
	}
}

func TestCodigoAleatorio(t *testing.T) {
	s := Novo(nil, nil)
	l, err := s.Criar("https://exemplo.com", "")
	if err != nil || !reCodigo.MatchString(l.Codigo) || len(l.Codigo) != 7 {
		t.Errorf("link %+v err %v", l, err)
	}
}

func TestResolverConcorrente(t *testing.T) {
	s := novoTeste()
	l, _ := s.Criar("http://x.com", "")
	var wg sync.WaitGroup
	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func() { defer wg.Done(); s.Resolver(l.Codigo) }()
	}
	wg.Wait()
	got, _ := s.Obter(l.Codigo)
	if got.Acessos != 100 {
		t.Errorf("acessos %d", got.Acessos)
	}
	var j map[string]any
	b, _ := json.Marshal(got)
	json.Unmarshal(b, &j)
	if j["criado_em"] == nil {
		t.Error("falta criado_em")
	}
}
