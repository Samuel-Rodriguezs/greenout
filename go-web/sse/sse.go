// Pacote sse implementa Server-Sent Events (alternativa simples a websockets)
// com um broker de publicação/assinatura.
package sse

import (
	"fmt"
	"io"
	"net/http"
	"strings"
	"sync"
)

// Evento é uma mensagem SSE.
type Evento struct {
	ID    string
	Nome  string
	Dados string
}

// Formatar serializa o evento no formato text/event-stream. Dados com várias
// linhas viram vários campos "data:".
func Formatar(e Evento) string {
	var b strings.Builder
	if e.ID != "" {
		fmt.Fprintf(&b, "id: %s\n", e.ID)
	}
	if e.Nome != "" {
		fmt.Fprintf(&b, "event: %s\n", e.Nome)
	}
	for _, l := range strings.Split(e.Dados, "\n") {
		fmt.Fprintf(&b, "data: %s\n", l)
	}
	b.WriteString("\n")
	return b.String()
}

// Broker distribui eventos a todos os assinantes.
type Broker struct {
	mu     sync.Mutex
	subs   map[chan Evento]struct{}
	Buffer int
}

// NovoBroker cria um broker com buffer por assinante.
func NovoBroker(buffer int) *Broker {
	return &Broker{subs: map[chan Evento]struct{}{}, Buffer: buffer}
}

// Inscrever registra um novo assinante.
func (b *Broker) Inscrever() chan Evento {
	ch := make(chan Evento, b.Buffer)
	b.mu.Lock()
	b.subs[ch] = struct{}{}
	b.mu.Unlock()
	return ch
}

// Cancelar remove e fecha o canal do assinante.
func (b *Broker) Cancelar(ch chan Evento) {
	b.mu.Lock()
	defer b.mu.Unlock()
	if _, ok := b.subs[ch]; ok {
		delete(b.subs, ch)
		close(ch)
	}
}

// Assinantes retorna o número de assinantes ativos.
func (b *Broker) Assinantes() int {
	b.mu.Lock()
	defer b.mu.Unlock()
	return len(b.subs)
}

// Publicar envia o evento a todos; assinantes lentos (buffer cheio) perdem a mensagem.
func (b *Broker) Publicar(e Evento) {
	b.mu.Lock()
	defer b.mu.Unlock()
	for ch := range b.subs {
		select {
		case ch <- e:
		default:
		}
	}
}

// Servir escreve eventos de fonte em w até o canal fechar ou o contexto da requisição acabar.
func Servir(w http.ResponseWriter, r *http.Request, fonte <-chan Evento) {
	f, ok := w.(http.Flusher)
	if !ok {
		http.Error(w, "streaming não suportado", http.StatusInternalServerError)
		return
	}
	h := w.Header()
	h.Set("Content-Type", "text/event-stream")
	h.Set("Cache-Control", "no-cache")
	h.Set("Connection", "keep-alive")
	w.WriteHeader(http.StatusOK)
	f.Flush()
	for {
		select {
		case <-r.Context().Done():
			return
		case e, ok := <-fonte:
			if !ok {
				return
			}
			io.WriteString(w, Formatar(e))
			f.Flush()
		}
	}
}

// Handler assina o broker durante a conexão.
func (b *Broker) Handler() http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		ch := b.Inscrever()
		defer b.Cancelar(ch)
		Servir(w, r, ch)
	})
}
