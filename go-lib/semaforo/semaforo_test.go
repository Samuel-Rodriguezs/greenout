package semaforo

import (
	"context"
	"errors"
	"sync"
	"sync/atomic"
	"testing"
	"time"
)

func TestTentarAdquirir(t *testing.T) {
	casos := []struct {
		nome string
		n    int
		want int // quantas aquisições bem-sucedidas em 5 tentativas
	}{
		{"uma vaga", 1, 1},
		{"tres vagas", 3, 3},
		{"invalido vira 1", 0, 1},
		{"negativo vira 1", -4, 1},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			s := Novo(c.n)
			ok := 0
			for i := 0; i < 5; i++ {
				if s.TentarAdquirir() {
					ok++
				}
			}
			if ok != c.want || s.EmUso() != c.want || s.Capacidade() != c.want {
				t.Fatalf("ok=%d emuso=%d cap=%d", ok, s.EmUso(), s.Capacidade())
			}
		})
	}
}

func TestLiberarSemAdquirirPanic(t *testing.T) {
	defer func() {
		if recover() == nil {
			t.Fatal("esperava panic")
		}
	}()
	Novo(1).Liberar()
}

func TestAdquirirContexto(t *testing.T) {
	s := Novo(1)
	if err := s.Adquirir(context.Background()); err != nil {
		t.Fatal(err)
	}
	ctx, cancel := context.WithTimeout(context.Background(), 20*time.Millisecond)
	defer cancel()
	if err := s.Adquirir(ctx); !errors.Is(err, context.DeadlineExceeded) {
		t.Fatalf("err=%v", err)
	}
	s.Liberar()
	cancelado, cancel2 := context.WithCancel(context.Background())
	cancel2()
	if err := s.Adquirir(cancelado); !errors.Is(err, context.Canceled) || s.EmUso() != 0 {
		t.Fatalf("ctx cancelado não pode adquirir: err=%v emuso=%d", err, s.EmUso())
	}
}

func TestAdquirirDesbloqueiaAoLiberar(t *testing.T) {
	s := Novo(1)
	s.TentarAdquirir()
	feito := make(chan error, 1)
	go func() { feito <- s.Adquirir(context.Background()) }()
	select {
	case <-feito:
		t.Fatal("não deveria ter adquirido ainda")
	case <-time.After(20 * time.Millisecond):
	}
	s.Liberar()
	if err := <-feito; err != nil {
		t.Fatal(err)
	}
}

func TestLimiteDeConcorrencia(t *testing.T) {
	const limite = 3
	s := Novo(limite)
	var atual, pico atomic.Int32
	var wg sync.WaitGroup
	for i := 0; i < 20; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			if err := s.Adquirir(context.Background()); err != nil {
				return
			}
			defer s.Liberar()
			n := atual.Add(1)
			for {
				p := pico.Load()
				if n <= p || pico.CompareAndSwap(p, n) {
					break
				}
			}
			time.Sleep(time.Millisecond)
			atual.Add(-1)
		}()
	}
	wg.Wait()
	if pico.Load() > limite || s.EmUso() != 0 {
		t.Fatalf("pico=%d emuso=%d", pico.Load(), s.EmUso())
	}
}
