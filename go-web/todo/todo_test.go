package todo

import (
	"encoding/json"
	"net/http/httptest"
	"strings"
	"sync"
	"testing"
	"time"
)

func novaLista() *Lista {
	t0 := time.Unix(1700000000, 0).UTC()
	return Nova(func() time.Time { return t0 })
}

func TestFluxoHTTP(t *testing.T) {
	h := novaLista().Handler()
	passos := []struct {
		nome, metodo, caminho, corpo string
		status                       int
		contem                       string
	}{
		{"lista vazia", "GET", "/tarefas", "", 200, "[]"},
		{"cria 1", "POST", "/tarefas", `{"titulo":"estudar Go"}`, 201, `"id":1`},
		{"cria 2", "POST", "/tarefas", `{"titulo":"  lavar louça  "}`, 201, `"titulo":"lavar louça"`},
		{"cria 3", "POST", "/tarefas", `{"titulo":"correr"}`, 201, `"id":3`},
		{"título vazio", "POST", "/tarefas", `{"titulo":"   "}`, 400, "obrigatório"},
		{"título longo", "POST", "/tarefas", `{"titulo":"` + strings.Repeat("a", 101) + `"}`, 400, "100 caracteres"},
		{"JSON ruim", "POST", "/tarefas", `{`, 400, "JSON inválido"},
		{"obtém", "GET", "/tarefas/1", "", 200, "estudar Go"},
		{"id inválido", "GET", "/tarefas/x", "", 400, "id inválido"},
		{"não existe", "GET", "/tarefas/42", "", 404, "não encontrada"},
		{"renomeia", "PUT", "/tarefas/2", `{"titulo":"lavar roupa"}`, 200, "lavar roupa"},
		{"renomeia inexistente", "PUT", "/tarefas/9", `{"titulo":"x"}`, 404, "não encontrada"},
		{"conclui", "PATCH", "/tarefas/1/concluir", "", 200, `"concluida":true`},
		{"conclui outra", "PATCH", "/tarefas/3/concluir", `{"concluida":true}`, 200, `"concluida":true`},
		{"reabre", "PATCH", "/tarefas/3/concluir", `{"concluida":false}`, 200, `"concluida":false`},
		{"conclui inexistente", "PATCH", "/tarefas/9/concluir", "", 404, "não encontrada"},
		{"filtra concluídas", "GET", "/tarefas?concluida=true", "", 200, "estudar Go"},
		{"filtro inválido", "GET", "/tarefas?concluida=talvez", "", 400, "true ou false"},
		{"remove", "DELETE", "/tarefas/1", "", 204, ""},
		{"remove de novo", "DELETE", "/tarefas/1", "", 404, "não encontrada"},
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
		})
	}
}

func TestFiltroEPaginacao(t *testing.T) {
	l := novaLista()
	for _, s := range []string{"a", "b", "c", "d", "e"} {
		l.Adicionar(s)
	}
	l.Marcar(2, true)
	l.Marcar(4, true)
	h := l.Handler()
	casos := []struct {
		nome, query string
		ids         []int
		total       string
	}{
		{"todas", "", []int{1, 2, 3, 4, 5}, "5"},
		{"pendentes", "?concluida=false", []int{1, 3, 5}, "3"},
		{"concluídas", "?concluida=true", []int{2, 4}, "2"},
		{"página 2", "?per_page=2&page=2", []int{3, 4}, "5"},
		{"página além", "?per_page=2&page=9", []int{}, "5"},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			rec := httptest.NewRecorder()
			h.ServeHTTP(rec, httptest.NewRequest("GET", "/tarefas"+c.query, nil))
			var ts []Tarefa
			if err := json.Unmarshal(rec.Body.Bytes(), &ts); err != nil {
				t.Fatal(err)
			}
			if len(ts) != len(c.ids) {
				t.Fatalf("tarefas %v, esperado ids %v", ts, c.ids)
			}
			for i, id := range c.ids {
				if ts[i].ID != id {
					t.Errorf("posição %d: id %d, esperado %d", i, ts[i].ID, id)
				}
			}
			if got := rec.Header().Get("X-Total-Count"); got != c.total {
				t.Errorf("X-Total-Count %q, esperado %q", got, c.total)
			}
		})
	}
}

func TestAtualizadaEm(t *testing.T) {
	t0 := time.Unix(100, 0)
	agora := t0
	l := Nova(func() time.Time { return agora })
	tr, _ := l.Adicionar("x")
	agora = t0.Add(time.Hour)
	tr2, _ := l.Marcar(tr.ID, true)
	if !tr2.CriadaEm.Equal(t0) || !tr2.AtualizadaEm.Equal(t0.Add(time.Hour)) {
		t.Errorf("datas incorretas: %+v", tr2)
	}
}

func TestConcorrencia(t *testing.T) {
	l := novaLista()
	var wg sync.WaitGroup
	for i := 0; i < 60; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			tr, _ := l.Adicionar("t")
			l.Marcar(tr.ID, true)
			l.Listar(nil)
		}()
	}
	wg.Wait()
	if n := len(l.Listar(nil)); n != 60 {
		t.Errorf("len = %d", n)
	}
}
