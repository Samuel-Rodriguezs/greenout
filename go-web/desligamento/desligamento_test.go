package desligamento

import (
	"context"
	"errors"
	"net/http"
	"testing"
	"time"
)

// falso simula um servidor sem abrir portas.
type falso struct {
	parar       chan struct{}
	errListen   error // se não nulo, ListenAndServe retorna imediatamente
	errShutdown error
	demora      time.Duration // quanto o Shutdown leva
	chamouShut  bool
	prazo       time.Duration
}

func novoFalso() *falso { return &falso{parar: make(chan struct{})} }

func (f *falso) ListenAndServe() error {
	if f.errListen != nil {
		return f.errListen
	}
	<-f.parar
	return http.ErrServerClosed
}

func (f *falso) Shutdown(ctx context.Context) error {
	f.chamouShut = true
	if d, ok := ctx.Deadline(); ok {
		f.prazo = time.Until(d)
	}
	select {
	case <-time.After(f.demora):
	case <-ctx.Done():
		return ctx.Err()
	}
	close(f.parar)
	return f.errShutdown
}

func TestExecutar(t *testing.T) {
	casos := []struct {
		nome     string
		f        *falso
		cancelar bool
		prazo    time.Duration
		erro     error
		shutdown bool
	}{
		{"encerramento limpo", novoFalso(), true, time.Second, nil, true},
		{"falha ao escutar", &falso{errListen: errors.New("porta ocupada"), parar: make(chan struct{})}, false, time.Second, errors.New("porta ocupada"), false},
		{"shutdown estoura prazo", &falso{parar: make(chan struct{}), demora: time.Second}, true, 20 * time.Millisecond, context.DeadlineExceeded, true},
		{"erro no shutdown", &falso{parar: make(chan struct{}), errShutdown: errors.New("falha")}, true, time.Second, nil, true},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			ctx, cancel := context.WithCancel(context.Background())
			defer cancel()
			if c.cancelar {
				cancel()
			}
			err := Executar(ctx, c.f, c.prazo)
			switch {
			case c.nome == "erro no shutdown":
				// Shutdown retorna erro mas o fechamento já ocorreu.
				if err == nil || err.Error() != "falha" {
					t.Errorf("erro %v", err)
				}
			case c.erro == nil && err != nil:
				t.Errorf("erro inesperado: %v", err)
			case c.erro != nil && (err == nil || (!errors.Is(err, c.erro) && err.Error() != c.erro.Error())):
				t.Errorf("erro %v, esperado %v", err, c.erro)
			}
			if c.f.chamouShut != c.shutdown {
				t.Errorf("Shutdown chamado = %v", c.f.chamouShut)
			}
		})
	}
}

func TestPrazoRespeitado(t *testing.T) {
	f := novoFalso()
	ctx, cancel := context.WithCancel(context.Background())
	cancel()
	if err := Executar(ctx, f, 5*time.Second); err != nil {
		t.Fatal(err)
	}
	if f.prazo <= 0 || f.prazo > 5*time.Second {
		t.Errorf("prazo do Shutdown = %v", f.prazo)
	}
}
