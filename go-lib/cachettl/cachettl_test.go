package cachettl

import (
	"sync"
	"testing"
	"time"
)

type relogio struct {
	mu sync.Mutex
	t  time.Time
}

func (r *relogio) Agora() time.Time {
	r.mu.Lock()
	defer r.mu.Unlock()
	return r.t
}

func (r *relogio) Avancar(d time.Duration) {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.t = r.t.Add(d)
}

func novoRelogio() *relogio { return &relogio{t: time.Date(2026, 1, 1, 0, 0, 0, 0, time.UTC)} }

func TestExpiracao(t *testing.T) {
	casos := []struct {
		nome   string
		ttl    time.Duration
		avanco time.Duration
		existe bool
	}{
		{"antes do ttl", 10 * time.Second, 9 * time.Second, true},
		{"exatamente no ttl", 10 * time.Second, 10 * time.Second, false},
		{"depois do ttl", 10 * time.Second, time.Minute, false},
		{"sem ttl nunca expira", 0, 24 * time.Hour, true},
		{"ttl negativo nunca expira", -1, 24 * time.Hour, true},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			r := novoRelogio()
			cache := Novo[string, int](r.Agora)
			cache.Definir("a", 1, c.ttl)
			r.Avancar(c.avanco)
			v, ok := cache.Obter("a")
			if ok != c.existe || (ok && v != 1) {
				t.Fatalf("ok=%v v=%d", ok, v)
			}
		})
	}
}

func TestSobrescreveRenovaTTL(t *testing.T) {
	r := novoRelogio()
	c := Novo[string, int](r.Agora)
	c.Definir("a", 1, 10*time.Second)
	r.Avancar(8 * time.Second)
	c.Definir("a", 2, 10*time.Second)
	r.Avancar(8 * time.Second)
	if v, ok := c.Obter("a"); !ok || v != 2 {
		t.Fatalf("v=%d ok=%v", v, ok)
	}
}

func TestRemoverELimpar(t *testing.T) {
	r := novoRelogio()
	c := Novo[string, int](r.Agora)
	c.Definir("curta", 1, time.Second)
	c.Definir("longa", 2, time.Hour)
	c.Definir("eterna", 3, 0)
	c.Definir("x", 4, time.Hour)
	c.Remover("x")
	c.Remover("inexistente")
	if c.Tamanho() != 3 {
		t.Fatalf("tamanho %d", c.Tamanho())
	}
	r.Avancar(2 * time.Second)
	if n := c.LimparExpirados(); n != 1 {
		t.Fatalf("limpou %d", n)
	}
	if c.Tamanho() != 2 {
		t.Fatalf("tamanho %d", c.Tamanho())
	}
	if _, ok := c.Obter("ausente"); ok {
		t.Fatal("chave ausente")
	}
}

func TestRelogioPadrao(t *testing.T) {
	c := Novo[int, int](nil)
	c.Definir(1, 1, time.Hour)
	if _, ok := c.Obter(1); !ok {
		t.Fatal("deveria existir")
	}
}

func TestConcorrencia(t *testing.T) {
	c := Novo[int, int](nil)
	var wg sync.WaitGroup
	for g := 0; g < 8; g++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for i := 0; i < 200; i++ {
				c.Definir(i, i, time.Minute)
				c.Obter(i)
				c.LimparExpirados()
			}
		}()
	}
	wg.Wait()
	if c.Tamanho() != 200 {
		t.Fatalf("tamanho %d", c.Tamanho())
	}
}
