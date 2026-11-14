// Pacote balde implementa os dois algoritmos clássicos de limitação de
// taxa: token bucket (permite rajadas até a capacidade) e leaky bucket como
// medidor (suaviza a saída a uma taxa constante). Ambos usam relógio injetável.
package balde

import (
	"sync"
	"time"
)

// Relogio devolve o instante atual.
type Relogio func() time.Time

// TokenBucket acumula fichas a taxa constante até uma capacidade máxima;
// cada operação consome fichas. É seguro para uso concorrente.
type TokenBucket struct {
	mu         sync.Mutex
	capacidade float64
	taxa       float64 // fichas por segundo
	fichas     float64
	ultimo     time.Time
	agora      Relogio
}

// NovoTokenBucket cria um balde cheio. capacidade e taxa devem ser positivas.
func NovoTokenBucket(capacidade, taxa float64, relogio Relogio) *TokenBucket {
	if relogio == nil {
		relogio = time.Now
	}
	return &TokenBucket{capacidade: capacidade, taxa: taxa, fichas: capacidade, ultimo: relogio(), agora: relogio}
}

func (b *TokenBucket) reabastece() {
	agora := b.agora()
	if dt := agora.Sub(b.ultimo).Seconds(); dt > 0 {
		b.fichas = min(b.capacidade, b.fichas+dt*b.taxa)
		b.ultimo = agora
	}
}

// Permitir tenta consumir n fichas. Devolve false (sem consumir nada) se não
// houver fichas suficientes ou se n exceder a capacidade.
func (b *TokenBucket) Permitir(n float64) bool {
	b.mu.Lock()
	defer b.mu.Unlock()
	b.reabastece()
	if n <= 0 || n > b.fichas {
		return n <= 0
	}
	b.fichas -= n
	return true
}

// Espera devolve quanto falta para haver n fichas disponíveis (0 se já há).
// Devolve -1 se n é maior que a capacidade, caso em que nunca será possível.
func (b *TokenBucket) Espera(n float64) time.Duration {
	b.mu.Lock()
	defer b.mu.Unlock()
	if n > b.capacidade {
		return -1
	}
	b.reabastece()
	if b.fichas >= n {
		return 0
	}
	return time.Duration((n - b.fichas) / b.taxa * float64(time.Second))
}

// Fichas devolve a quantidade atual de fichas.
func (b *TokenBucket) Fichas() float64 {
	b.mu.Lock()
	defer b.mu.Unlock()
	b.reabastece()
	return b.fichas
}

// LeakyBucket modela um balde com furo: cada requisição acrescenta água e o
// nível vaza a taxa constante. Requisições que fariam o balde transbordar
// são rejeitadas. É seguro para uso concorrente.
type LeakyBucket struct {
	mu         sync.Mutex
	capacidade float64
	taxa       float64 // unidades que vazam por segundo
	nivel      float64
	ultimo     time.Time
	agora      Relogio
}

// NovoLeakyBucket cria um balde vazio.
func NovoLeakyBucket(capacidade, taxa float64, relogio Relogio) *LeakyBucket {
	if relogio == nil {
		relogio = time.Now
	}
	return &LeakyBucket{capacidade: capacidade, taxa: taxa, ultimo: relogio(), agora: relogio}
}

func (b *LeakyBucket) vaza() {
	agora := b.agora()
	if dt := agora.Sub(b.ultimo).Seconds(); dt > 0 {
		b.nivel = max(0, b.nivel-dt*b.taxa)
		b.ultimo = agora
	}
}

// Adicionar tenta despejar n unidades no balde. Devolve false, sem alterar o
// nível, se transbordaria.
func (b *LeakyBucket) Adicionar(n float64) bool {
	b.mu.Lock()
	defer b.mu.Unlock()
	b.vaza()
	if n < 0 || b.nivel+n > b.capacidade {
		return false
	}
	b.nivel += n
	return true
}

// Nivel devolve o nível atual do balde.
func (b *LeakyBucket) Nivel() float64 {
	b.mu.Lock()
	defer b.mu.Unlock()
	b.vaza()
	return b.nivel
}
