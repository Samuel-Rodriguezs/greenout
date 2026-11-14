// Pacote limitador implementa rate limiting por IP com janela fixa e relógio injetável.
package limitador

import (
	"net"
	"net/http"
	"strconv"
	"sync"
	"time"
)

type janela struct {
	inicio time.Time
	conta  int
}

// Limitador permite até Max requisições por IP a cada Janela.
type Limitador struct {
	Max    int
	Janela time.Duration
	Agora  func() time.Time

	mu      sync.Mutex
	janelas map[string]*janela
}

// Novo cria um limitador. agora nulo usa time.Now.
func Novo(max int, jan time.Duration, agora func() time.Time) *Limitador {
	if agora == nil {
		agora = time.Now
	}
	return &Limitador{Max: max, Janela: jan, Agora: agora, janelas: map[string]*janela{}}
}

// Permitir registra uma requisição do IP e informa se é permitida, quantas
// restam e quanto falta para a janela renovar.
func (l *Limitador) Permitir(ip string) (ok bool, restam int, renova time.Duration) {
	l.mu.Lock()
	defer l.mu.Unlock()
	agora := l.Agora()
	j := l.janelas[ip]
	if j == nil || agora.Sub(j.inicio) >= l.Janela {
		j = &janela{inicio: agora}
		l.janelas[ip] = j
	}
	renova = l.Janela - agora.Sub(j.inicio)
	if j.conta >= l.Max {
		return false, 0, renova
	}
	j.conta++
	return true, l.Max - j.conta, renova
}

func ipDe(r *http.Request) string {
	h, _, err := net.SplitHostPort(r.RemoteAddr)
	if err != nil {
		return r.RemoteAddr
	}
	return h
}

// Middleware aplica o limite e responde 429 com Retry-After quando excedido.
func (l *Limitador) Middleware(prox http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		ok, restam, renova := l.Permitir(ipDe(r))
		w.Header().Set("X-RateLimit-Remaining", strconv.Itoa(restam))
		if !ok {
			seg := int(renova.Seconds())
			if renova%time.Second != 0 {
				seg++
			}
			w.Header().Set("Retry-After", strconv.Itoa(seg))
			http.Error(w, "muitas requisições", http.StatusTooManyRequests)
			return
		}
		prox.ServeHTTP(w, r)
	})
}
