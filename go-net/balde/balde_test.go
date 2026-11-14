package balde

import (
	"math"
	"sync"
	"testing"
	"time"
)

type relogio struct{ t time.Time }

func (r *relogio) Agora() time.Time       { return r.t }
func (r *relogio) Avanca(d time.Duration) { r.t = r.t.Add(d) }
func novoRelogio() *relogio               { return &relogio{time.Date(2026, 1, 1, 0, 0, 0, 0, time.UTC)} }

func perto(a, b float64) bool { return math.Abs(a-b) < 1e-9 }

func TestTokenBucketRajadaELimite(t *testing.T) {
	r := novoRelogio()
	b := NovoTokenBucket(5, 1, r.Agora)
	for i := 0; i < 5; i++ {
		if !b.Permitir(1) {
			t.Fatalf("rajada %d deveria passar", i)
		}
	}
	if b.Permitir(1) {
		t.Error("balde vazio deveria negar")
	}
	r.Avanca(2 * time.Second)
	if !b.Permitir(2) || b.Permitir(1) {
		t.Error("após 2s deveria haver exatamente 2 fichas")
	}
}

func TestTokenBucketNaoExcedeCapacidade(t *testing.T) {
	r := novoRelogio()
	b := NovoTokenBucket(3, 10, r.Agora)
	r.Avanca(time.Hour)
	if !perto(b.Fichas(), 3) {
		t.Errorf("Fichas = %v, esperava 3", b.Fichas())
	}
	if b.Permitir(4) {
		t.Error("mais que a capacidade nunca passa")
	}
	if !perto(b.Fichas(), 3) {
		t.Error("negar não deve consumir")
	}
}

func TestTokenBucketFracionado(t *testing.T) {
	r := novoRelogio()
	b := NovoTokenBucket(10, 2, r.Agora) // 2 fichas/s
	b.Permitir(10)
	r.Avanca(250 * time.Millisecond)
	if !perto(b.Fichas(), 0.5) {
		t.Errorf("Fichas = %v, esperava 0.5", b.Fichas())
	}
	if b.Permitir(1) {
		t.Error("meia ficha não basta")
	}
	r.Avanca(250 * time.Millisecond)
	if !b.Permitir(1) {
		t.Error("deveria ter 1 ficha")
	}
}

func TestTokenBucketEspera(t *testing.T) {
	r := novoRelogio()
	b := NovoTokenBucket(10, 4, r.Agora)
	if b.Espera(10) != 0 {
		t.Error("balde cheio não espera")
	}
	b.Permitir(10)
	if got := b.Espera(2); got != 500*time.Millisecond {
		t.Errorf("Espera(2) = %v", got)
	}
	r.Avanca(250 * time.Millisecond)
	if got := b.Espera(2); got != 250*time.Millisecond {
		t.Errorf("Espera(2) após 250ms = %v", got)
	}
	if b.Espera(11) != -1 {
		t.Error("acima da capacidade deveria devolver -1")
	}
}

func TestTokenBucketZeroEmNegativo(t *testing.T) {
	b := NovoTokenBucket(1, 1, novoRelogio().Agora)
	if !b.Permitir(0) {
		t.Error("consumir 0 é sempre permitido")
	}
	if b.Permitir(-1) != true {
		t.Error("n <= 0 é um no-op permitido")
	}
	if !perto(b.Fichas(), 1) {
		t.Error("no-op não consome")
	}
}

func TestLeakyBucket(t *testing.T) {
	r := novoRelogio()
	b := NovoLeakyBucket(4, 2, r.Agora) // vaza 2/s
	for i := 0; i < 4; i++ {
		if !b.Adicionar(1) {
			t.Fatalf("adicionar %d deveria caber", i)
		}
	}
	if b.Adicionar(1) {
		t.Error("deveria transbordar")
	}
	if !perto(b.Nivel(), 4) {
		t.Errorf("nível = %v (rejeição não deve alterar)", b.Nivel())
	}
}

func TestLeakyBucketVazamento(t *testing.T) {
	r := novoRelogio()
	b := NovoLeakyBucket(10, 2, r.Agora)
	b.Adicionar(10)
	r.Avanca(3 * time.Second)
	if !perto(b.Nivel(), 4) {
		t.Errorf("nível após 3s = %v, esperava 4", b.Nivel())
	}
	if !b.Adicionar(6) || b.Adicionar(0.5) {
		t.Error("deveria caber 6 e depois transbordar")
	}
	r.Avanca(time.Hour)
	if b.Nivel() != 0 {
		t.Errorf("nível nunca fica negativo: %v", b.Nivel())
	}
	if b.Adicionar(11) || b.Adicionar(-1) {
		t.Error("valores inválidos devem ser rejeitados")
	}
}

func TestTaxaConstanteAoLongoDoTempo(t *testing.T) {
	r := novoRelogio()
	b := NovoTokenBucket(1, 10, r.Agora) // 10 req/s, sem rajada
	b.Permitir(1)
	aceitas := 0
	for i := 0; i < 1000; i++ { // 50 s em passos de 50 ms (0,5 ficha por passo)
		r.Avanca(50 * time.Millisecond)
		if b.Permitir(1) {
			aceitas++
		}
	}
	if aceitas < 499 || aceitas > 501 {
		t.Errorf("aceitas = %d, esperava ~500", aceitas)
	}
}

func TestConcorrencia(t *testing.T) {
	tb := NovoTokenBucket(1000, 0.001, nil)
	lb := NovoLeakyBucket(1000, 0.001, nil)
	var wg sync.WaitGroup
	var mu sync.Mutex
	passou := 0
	for i := 0; i < 8; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := 0; j < 200; j++ {
				if tb.Permitir(1) {
					mu.Lock()
					passou++
					mu.Unlock()
				}
				lb.Adicionar(1)
			}
		}()
	}
	wg.Wait()
	if passou < 1000 || passou > 1001 {
		t.Errorf("passaram %d, esperava 1000 (capacidade)", passou)
	}
}
