package sse

import (
	"context"
	"net/http/httptest"
	"strings"
	"testing"
	"time"
)

func TestFormatar(t *testing.T) {
	casos := []struct {
		nome     string
		e        Evento
		esperado string
	}{
		{"só dados", Evento{Dados: "oi"}, "data: oi\n\n"},
		{"completo", Evento{ID: "7", Nome: "msg", Dados: "oi"}, "id: 7\nevent: msg\ndata: oi\n\n"},
		{"multilinha", Evento{Dados: "a\nb"}, "data: a\ndata: b\n\n"},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := Formatar(c.e); got != c.esperado {
				t.Errorf("Formatar = %q, esperado %q", got, c.esperado)
			}
		})
	}
}

func TestServirCanalFechado(t *testing.T) {
	fonte := make(chan Evento, 3)
	fonte <- Evento{Nome: "a", Dados: "1"}
	fonte <- Evento{Dados: "2"}
	close(fonte)
	rec := httptest.NewRecorder()
	Servir(rec, httptest.NewRequest("GET", "/eventos", nil), fonte)
	if ct := rec.Header().Get("Content-Type"); ct != "text/event-stream" {
		t.Errorf("Content-Type %q", ct)
	}
	if esperado := "event: a\ndata: 1\n\ndata: 2\n\n"; rec.Body.String() != esperado {
		t.Errorf("corpo %q, esperado %q", rec.Body.String(), esperado)
	}
	if !rec.Flushed {
		t.Error("deveria ter dado flush")
	}
}

func TestBrokerHandler(t *testing.T) {
	b := NovoBroker(4)
	ctx, cancelar := context.WithCancel(context.Background())
	req := httptest.NewRequest("GET", "/eventos", nil).WithContext(ctx)
	rec := httptest.NewRecorder()
	pronto := make(chan struct{})
	go func() {
		defer close(pronto)
		b.Handler().ServeHTTP(rec, req)
	}()
	for b.Assinantes() == 0 {
		time.Sleep(time.Millisecond)
	}
	b.Publicar(Evento{Nome: "x", Dados: "um"})
	b.Publicar(Evento{Dados: "dois"})
	// Aguarda o handler consumir os eventos (fila vazia) antes de cancelar.
	b.mu.Lock()
	var ch chan Evento
	for c := range b.subs {
		ch = c
	}
	b.mu.Unlock()
	for len(ch) > 0 {
		time.Sleep(time.Millisecond)
	}
	cancelar()
	<-pronto
	if b.Assinantes() != 0 {
		t.Error("assinante deveria ter sido removido")
	}
	// O handler pode ter retirado o 2º evento do canal mas ainda não escrito;
	// após <-pronto a escrita já ocorreu ou o contexto venceu a disputa.
	corpo := rec.Body.String()
	if !strings.HasPrefix(corpo, "event: x\ndata: um\n\n") {
		t.Errorf("corpo inesperado: %q", corpo)
	}
}

func TestBrokerPublicarSemBloquear(t *testing.T) {
	b := NovoBroker(1)
	ch := b.Inscrever()
	b.Publicar(Evento{Dados: "1"})
	b.Publicar(Evento{Dados: "2"}) // buffer cheio: descartado, não bloqueia
	if len(ch) != 1 {
		t.Errorf("len = %d", len(ch))
	}
	b.Cancelar(ch)
	b.Cancelar(ch) // idempotente
	if b.Assinantes() != 0 {
		t.Error("deveria estar vazio")
	}
}
