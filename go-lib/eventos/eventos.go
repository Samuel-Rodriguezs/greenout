// Pacote eventos implementa um barramento de eventos tipado e seguro para concorrência.
package eventos

import "sync"

type assinante[E any] struct {
	id int
	f  func(E)
}

// Barramento entrega cada evento publicado a todos os assinantes, em ordem de inscrição.
type Barramento[E any] struct {
	mu      sync.RWMutex
	prox    int
	assinas []assinante[E]
}

// Inscrever registra um tratador e devolve a função que cancela a inscrição.
func (b *Barramento[E]) Inscrever(f func(E)) (cancelar func()) {
	b.mu.Lock()
	defer b.mu.Unlock()
	id := b.prox
	b.prox++
	b.assinas = append(b.assinas, assinante[E]{id: id, f: f})
	var once sync.Once
	return func() {
		once.Do(func() {
			b.mu.Lock()
			defer b.mu.Unlock()
			for i, a := range b.assinas {
				if a.id == id {
					b.assinas = append(b.assinas[:i:i], b.assinas[i+1:]...)
					return
				}
			}
		})
	}
}

// Publicar chama sincronicamente cada assinante. Tratadores podem se
// inscrever/cancelar durante a entrega: a lista é copiada antes de iterar.
// Devolve quantos assinantes receberam o evento.
func (b *Barramento[E]) Publicar(e E) int {
	b.mu.RLock()
	copia := make([]assinante[E], len(b.assinas))
	copy(copia, b.assinas)
	b.mu.RUnlock()
	for _, a := range copia {
		a.f(e)
	}
	return len(copia)
}

// Assinantes devolve a quantidade de assinantes atuais.
func (b *Barramento[E]) Assinantes() int {
	b.mu.RLock()
	defer b.mu.RUnlock()
	return len(b.assinas)
}
