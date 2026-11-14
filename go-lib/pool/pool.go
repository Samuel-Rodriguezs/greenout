// Pacote pool implementa um pool de objetos reutilizáveis com limite de ociosos.
package pool

import "sync"

// Pool guarda até max objetos ociosos para reutilização.
type Pool[T any] struct {
	mu       sync.Mutex
	livres   []T
	max      int
	criar    func() T
	resetar  func(T)
	criados  int
	reusados int
}

// Novo cria um pool. criar é obrigatório; resetar (opcional) prepara o objeto
// devolvido para reuso; max limita quantos objetos ociosos são retidos.
func Novo[T any](max int, criar func() T, resetar func(T)) *Pool[T] {
	if criar == nil {
		panic("pool: função criar é obrigatória")
	}
	return &Pool[T]{max: max, criar: criar, resetar: resetar}
}

// Obter devolve um objeto ocioso ou cria um novo.
func (p *Pool[T]) Obter() T {
	p.mu.Lock()
	if n := len(p.livres); n > 0 {
		v := p.livres[n-1]
		var zero T
		p.livres[n-1] = zero
		p.livres = p.livres[:n-1]
		p.reusados++
		p.mu.Unlock()
		return v
	}
	p.criados++
	p.mu.Unlock()
	return p.criar()
}

// Devolver reseta o objeto e o guarda; descarta se o pool já estiver cheio.
// Retorna true se o objeto foi retido.
func (p *Pool[T]) Devolver(v T) bool {
	if p.resetar != nil {
		p.resetar(v)
	}
	p.mu.Lock()
	defer p.mu.Unlock()
	if len(p.livres) >= p.max {
		return false
	}
	p.livres = append(p.livres, v)
	return true
}

// Ociosos devolve quantos objetos estão disponíveis.
func (p *Pool[T]) Ociosos() int {
	p.mu.Lock()
	defer p.mu.Unlock()
	return len(p.livres)
}

// Estatisticas devolve quantos objetos foram criados e reutilizados.
func (p *Pool[T]) Estatisticas() (criados, reusados int) {
	p.mu.Lock()
	defer p.mu.Unlock()
	return p.criados, p.reusados
}
