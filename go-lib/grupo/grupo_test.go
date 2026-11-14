package grupo

import (
	"context"
	"errors"
	"sync/atomic"
	"testing"
	"time"
)

func TestSemErro(t *testing.T) {
	g := Novo()
	var n atomic.Int32
	for i := 0; i < 10; i++ {
		g.Go(func() error { n.Add(1); return nil })
	}
	if err := g.Esperar(); err != nil || n.Load() != 10 {
		t.Fatalf("err=%v n=%d", err, n.Load())
	}
}

func TestGrupoVazio(t *testing.T) {
	if err := Novo().Esperar(); err != nil {
		t.Fatal(err)
	}
}

func TestPrimeiroErro(t *testing.T) {
	primeiro := errors.New("primeiro")
	g := Novo()
	g.Go(func() error { return primeiro })
	g.Go(func() error { time.Sleep(50 * time.Millisecond); return errors.New("depois") })
	g.Go(func() error { return nil })
	if err := g.Esperar(); !errors.Is(err, primeiro) {
		t.Fatalf("err=%v", err)
	}
}

func TestContextoCanceladoNoErro(t *testing.T) {
	g, ctx := ComContexto(context.Background())
	boom := errors.New("boom")
	g.Go(func() error { return boom })
	g.Go(func() error {
		select {
		case <-ctx.Done():
			return nil
		case <-time.After(5 * time.Second):
			return errors.New("contexto não foi cancelado")
		}
	})
	if err := g.Esperar(); !errors.Is(err, boom) {
		t.Fatalf("err=%v", err)
	}
	if ctx.Err() == nil {
		t.Fatal("contexto deveria estar cancelado após Esperar")
	}
}

func TestContextoCanceladoSemErro(t *testing.T) {
	g, ctx := ComContexto(context.Background())
	g.Go(func() error { return nil })
	if err := g.Esperar(); err != nil || ctx.Err() == nil {
		t.Fatalf("err=%v ctx=%v", err, ctx.Err())
	}
}

func TestLimitar(t *testing.T) {
	casos := []struct {
		nome   string
		limite int
		maximo int32
	}{
		{"limite 1", 1, 1},
		{"limite 3", 3, 3},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			g := Novo()
			g.Limitar(c.limite)
			var atual, pico atomic.Int32
			for i := 0; i < 12; i++ {
				g.Go(func() error {
					n := atual.Add(1)
					for {
						p := pico.Load()
						if n <= p || pico.CompareAndSwap(p, n) {
							break
						}
					}
					time.Sleep(2 * time.Millisecond)
					atual.Add(-1)
					return nil
				})
			}
			if err := g.Esperar(); err != nil {
				t.Fatal(err)
			}
			if pico.Load() > c.maximo {
				t.Fatalf("pico %d > %d", pico.Load(), c.maximo)
			}
		})
	}
	g := Novo()
	g.Limitar(2)
	g.Limitar(0) // remove limite
	g.Go(func() error { return nil })
	if err := g.Esperar(); err != nil {
		t.Fatal(err)
	}
}
