// Pacote skiplist implementa uma skip list ordenada, segura para uso
// concorrente, com gerador aleatório determinístico (semente injetável).
package skiplist

import (
	"cmp"
	"math/rand"
	"sync"
)

const (
	nivelMaximo   = 24
	probabilidade = 0.5
)

type no[K cmp.Ordered, V any] struct {
	chave K
	valor V
	prox  []*no[K, V]
}

// Lista é uma skip list ordenada por K.
type Lista[K cmp.Ordered, V any] struct {
	mu    sync.RWMutex
	cab   *no[K, V]
	nivel int
	n     int
	rng   *rand.Rand
}

// Nova cria uma lista; a semente torna a estrutura reproduzível.
func Nova[K cmp.Ordered, V any](semente int64) *Lista[K, V] {
	return &Lista[K, V]{
		cab:   &no[K, V]{prox: make([]*no[K, V], nivelMaximo)},
		nivel: 1,
		rng:   rand.New(rand.NewSource(semente)),
	}
}

func (l *Lista[K, V]) nivelAleatorio() int {
	n := 1
	for n < nivelMaximo && l.rng.Float64() < probabilidade {
		n++
	}
	return n
}

// Tamanho devolve a quantidade de chaves.
func (l *Lista[K, V]) Tamanho() int {
	l.mu.RLock()
	defer l.mu.RUnlock()
	return l.n
}

// buscarAnteriores preenche ant com o último nó < k em cada nível.
func (l *Lista[K, V]) buscarAnteriores(k K, ant *[nivelMaximo]*no[K, V]) *no[K, V] {
	x := l.cab
	for i := l.nivel - 1; i >= 0; i-- {
		for x.prox[i] != nil && x.prox[i].chave < k {
			x = x.prox[i]
		}
		if ant != nil {
			ant[i] = x
		}
	}
	return x.prox[0]
}

// Buscar procura a chave.
func (l *Lista[K, V]) Buscar(k K) (V, bool) {
	l.mu.RLock()
	defer l.mu.RUnlock()
	if c := l.buscarAnteriores(k, nil); c != nil && c.chave == k {
		return c.valor, true
	}
	var z V
	return z, false
}

// Inserir grava k=v; devolve true se a chave era nova.
func (l *Lista[K, V]) Inserir(k K, v V) bool {
	l.mu.Lock()
	defer l.mu.Unlock()
	var ant [nivelMaximo]*no[K, V]
	c := l.buscarAnteriores(k, &ant)
	if c != nil && c.chave == k {
		c.valor = v
		return false
	}
	nv := l.nivelAleatorio()
	if nv > l.nivel {
		for i := l.nivel; i < nv; i++ {
			ant[i] = l.cab
		}
		l.nivel = nv
	}
	novo := &no[K, V]{chave: k, valor: v, prox: make([]*no[K, V], nv)}
	for i := 0; i < nv; i++ {
		novo.prox[i] = ant[i].prox[i]
		ant[i].prox[i] = novo
	}
	l.n++
	return true
}

// Remover apaga a chave; devolve true se existia.
func (l *Lista[K, V]) Remover(k K) bool {
	l.mu.Lock()
	defer l.mu.Unlock()
	var ant [nivelMaximo]*no[K, V]
	c := l.buscarAnteriores(k, &ant)
	if c == nil || c.chave != k {
		return false
	}
	for i := 0; i < l.nivel; i++ {
		if ant[i].prox[i] != c {
			break
		}
		ant[i].prox[i] = c.prox[i]
	}
	for l.nivel > 1 && l.cab.prox[l.nivel-1] == nil {
		l.nivel--
	}
	l.n--
	return true
}

// Percorrer visita todas as chaves em ordem; para se fn devolver false.
// A lista fica travada para leitura durante a visita: fn não pode escrever.
func (l *Lista[K, V]) Percorrer(fn func(K, V) bool) {
	l.mu.RLock()
	defer l.mu.RUnlock()
	for x := l.cab.prox[0]; x != nil; x = x.prox[0] {
		if !fn(x.chave, x.valor) {
			return
		}
	}
}

// Intervalo visita as chaves em [de, ate) em ordem.
func (l *Lista[K, V]) Intervalo(de, ate K, fn func(K, V) bool) {
	l.mu.RLock()
	defer l.mu.RUnlock()
	for x := l.buscarAnteriores(de, nil); x != nil && x.chave < ate; x = x.prox[0] {
		if !fn(x.chave, x.valor) {
			return
		}
	}
}

// Minimo devolve a menor chave.
func (l *Lista[K, V]) Minimo() (K, V, bool) {
	l.mu.RLock()
	defer l.mu.RUnlock()
	if x := l.cab.prox[0]; x != nil {
		return x.chave, x.valor, true
	}
	var k K
	var v V
	return k, v, false
}
