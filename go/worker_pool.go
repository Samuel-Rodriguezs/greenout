package lab

import (
	"errors"
	"sync"
)

// ErrPoolTrabalhadoresInvalido indica número de trabalhadores < 1.
var ErrPoolTrabalhadoresInvalido = errors.New("pool: trabalhadores deve ser >= 1")

// PoolExecutar aplica fn a cada entrada usando n goroutines e canais.
// O resultado é determinístico: saida[i] = fn(entradas[i]), independentemente
// da ordem de execução.
func PoolExecutar[E, S any](entradas []E, n int, fn func(E) S) ([]S, error) {
	if n < 1 {
		return nil, ErrPoolTrabalhadoresInvalido
	}
	saida := make([]S, len(entradas))
	tarefas := make(chan int)
	var wg sync.WaitGroup
	for w := 0; w < n; w++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for i := range tarefas {
				saida[i] = fn(entradas[i]) // cada índice é escrito por uma só goroutine
			}
		}()
	}
	for i := range entradas {
		tarefas <- i
	}
	close(tarefas)
	wg.Wait()
	return saida, nil
}
