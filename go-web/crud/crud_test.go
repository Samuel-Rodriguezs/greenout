package crud

import (
	"encoding/json"
	"net/http/httptest"
	"strings"
	"sync"
	"testing"
)

func TestAPI(t *testing.T) {
	h := API{Store: NovoStore()}.Handler()
	passos := []struct {
		nome, metodo, caminho, corpo string
		status                       int
		contem                       string
	}{
		{"lista vazia", "GET", "/itens", "", 200, "[]"},
		{"cria", "POST", "/itens", `{"nome":"caneta","preco":2.5}`, 201, `"id":1`},
		{"cria sem nome", "POST", "/itens", `{"preco":1}`, 400, "nome é obrigatório"},
		{"cria preço negativo", "POST", "/itens", `{"nome":"x","preco":-1}`, 400, "negativo"},
		{"cria JSON ruim", "POST", "/itens", `{`, 400, "JSON inválido"},
		{"campo desconhecido", "POST", "/itens", `{"nome":"x","foo":1}`, 400, "JSON inválido"},
		{"obtém", "GET", "/itens/1", "", 200, "caneta"},
		{"não existe", "GET", "/itens/99", "", 404, "não encontrado"},
		{"id inválido", "GET", "/itens/abc", "", 400, "id inválido"},
		{"atualiza", "PUT", "/itens/1", `{"nome":"lápis","preco":1}`, 200, "lápis"},
		{"atualiza inexistente", "PUT", "/itens/9", `{"nome":"x"}`, 404, "não encontrado"},
		{"lista", "GET", "/itens", "", 200, "lápis"},
		{"remove", "DELETE", "/itens/1", "", 204, ""},
		{"remove de novo", "DELETE", "/itens/1", "", 404, "não encontrado"},
		{"método inválido", "PATCH", "/itens/1", "", 405, ""},
	}
	for _, p := range passos {
		t.Run(p.nome, func(t *testing.T) {
			rec := httptest.NewRecorder()
			h.ServeHTTP(rec, httptest.NewRequest(p.metodo, p.caminho, strings.NewReader(p.corpo)))
			if rec.Code != p.status {
				t.Fatalf("status %d, esperado %d (%s)", rec.Code, p.status, rec.Body)
			}
			if !strings.Contains(rec.Body.String(), p.contem) {
				t.Errorf("corpo %q sem %q", rec.Body.String(), p.contem)
			}
		})
	}
}

func TestLocation(t *testing.T) {
	h := API{Store: NovoStore()}.Handler()
	rec := httptest.NewRecorder()
	h.ServeHTTP(rec, httptest.NewRequest("POST", "/itens", strings.NewReader(`{"nome":"a"}`)))
	if rec.Header().Get("Location") != "/itens/1" {
		t.Errorf("Location %q", rec.Header().Get("Location"))
	}
	var i Item
	json.Unmarshal(rec.Body.Bytes(), &i)
	if i.ID != 1 || i.Nome != "a" {
		t.Errorf("item %+v", i)
	}
}

func TestStoreConcorrente(t *testing.T) {
	s := NovoStore()
	var wg sync.WaitGroup
	for i := 0; i < 50; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			it := s.Criar(Item{Nome: "x"})
			s.Obter(it.ID)
			s.Listar()
		}()
	}
	wg.Wait()
	l := s.Listar()
	if len(l) != 50 {
		t.Fatalf("len = %d", len(l))
	}
	for i, it := range l {
		if it.ID != i+1 {
			t.Fatalf("IDs não sequenciais: %v", l)
		}
	}
}
