// Pacote saude implementa um endpoint de health check com verificações de dependências.
package saude

import (
	"context"
	"encoding/json"
	"net/http"
	"sort"
	"sync"
	"time"
)

// Verificacao testa uma dependência; erro nulo significa saudável.
type Verificacao func(ctx context.Context) error

// Checador agrega verificações nomeadas.
type Checador struct {
	Timeout time.Duration
	itens   map[string]Verificacao
}

// Novo cria um checador com timeout por verificação.
func Novo(timeout time.Duration) *Checador {
	return &Checador{Timeout: timeout, itens: map[string]Verificacao{}}
}

// Registrar adiciona uma verificação.
func (c *Checador) Registrar(nome string, v Verificacao) { c.itens[nome] = v }

// Relatorio é o resultado serializado.
type Relatorio struct {
	Status   string            `json:"status"`
	Detalhes map[string]string `json:"detalhes"`
}

// Executar roda todas as verificações em paralelo.
func (c *Checador) Executar(ctx context.Context) Relatorio {
	rel := Relatorio{Status: "ok", Detalhes: map[string]string{}}
	var mu sync.Mutex
	var wg sync.WaitGroup
	for nome, v := range c.itens {
		wg.Add(1)
		go func() {
			defer wg.Done()
			cctx, cancel := context.WithTimeout(ctx, c.Timeout)
			defer cancel()
			res := "ok"
			canal := make(chan error, 1)
			go func() { canal <- v(cctx) }()
			select {
			case err := <-canal:
				if err != nil {
					res = err.Error()
				}
			case <-cctx.Done():
				res = "timeout"
			}
			mu.Lock()
			rel.Detalhes[nome] = res
			if res != "ok" {
				rel.Status = "falha"
			}
			mu.Unlock()
		}()
	}
	wg.Wait()
	return rel
}

// Nomes lista as verificações registradas em ordem alfabética.
func (c *Checador) Nomes() []string {
	n := make([]string, 0, len(c.itens))
	for k := range c.itens {
		n = append(n, k)
	}
	sort.Strings(n)
	return n
}

// Handler responde 200 se tudo está ok ou 503 caso contrário.
func (c *Checador) Handler() http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		rel := c.Executar(r.Context())
		w.Header().Set("Content-Type", "application/json")
		if rel.Status != "ok" {
			w.WriteHeader(http.StatusServiceUnavailable)
		}
		json.NewEncoder(w).Encode(rel)
	})
}
