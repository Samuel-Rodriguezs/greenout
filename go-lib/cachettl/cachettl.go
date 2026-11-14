// Pacote cachettl implementa um cache em memória com expiração (TTL)
// e relógio injetável, seguro para uso concorrente.
package cachettl

import (
	"sync"
	"time"
)

type entrada[V any] struct {
	valor  V
	expira time.Time
}

// Cache guarda pares chave/valor que expiram após um TTL.
type Cache[K comparable, V any] struct {
	mu    sync.Mutex
	dados map[K]entrada[V]
	agora func() time.Time
}

// Novo cria um cache. Se agora for nil, usa time.Now.
func Novo[K comparable, V any](agora func() time.Time) *Cache[K, V] {
	if agora == nil {
		agora = time.Now
	}
	return &Cache[K, V]{dados: make(map[K]entrada[V]), agora: agora}
}

// Definir guarda o valor por ttl. ttl <= 0 significa que nunca expira.
func (c *Cache[K, V]) Definir(k K, v V, ttl time.Duration) {
	c.mu.Lock()
	defer c.mu.Unlock()
	e := entrada[V]{valor: v}
	if ttl > 0 {
		e.expira = c.agora().Add(ttl)
	}
	c.dados[k] = e
}

func (e entrada[V]) vencida(agora time.Time) bool {
	return !e.expira.IsZero() && !agora.Before(e.expira)
}

// Obter devolve o valor se existir e não tiver expirado.
func (c *Cache[K, V]) Obter(k K) (v V, ok bool) {
	c.mu.Lock()
	defer c.mu.Unlock()
	e, existe := c.dados[k]
	if !existe {
		return v, false
	}
	if e.vencida(c.agora()) {
		delete(c.dados, k)
		return v, false
	}
	return e.valor, true
}

// Remover apaga a chave.
func (c *Cache[K, V]) Remover(k K) {
	c.mu.Lock()
	defer c.mu.Unlock()
	delete(c.dados, k)
}

// LimparExpirados apaga as entradas vencidas e devolve quantas foram removidas.
func (c *Cache[K, V]) LimparExpirados() int {
	c.mu.Lock()
	defer c.mu.Unlock()
	agora := c.agora()
	n := 0
	for k, e := range c.dados {
		if e.vencida(agora) {
			delete(c.dados, k)
			n++
		}
	}
	return n
}

// Tamanho devolve o número de entradas armazenadas (inclui vencidas ainda não limpas).
func (c *Cache[K, V]) Tamanho() int {
	c.mu.Lock()
	defer c.mu.Unlock()
	return len(c.dados)
}
