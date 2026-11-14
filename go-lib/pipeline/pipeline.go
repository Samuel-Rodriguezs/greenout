// Pacote pipeline oferece blocos para montar pipelines de channels:
// geração, transformação, fan-out (vários workers) e fan-in (mesclagem).
package pipeline

import (
	"context"
	"sync"
)

// Gerar emite os valores em um channel e o fecha ao terminar ou ao cancelar ctx.
func Gerar[T any](ctx context.Context, valores ...T) <-chan T {
	out := make(chan T)
	go func() {
		defer close(out)
		for _, v := range valores {
			select {
			case out <- v:
			case <-ctx.Done():
				return
			}
		}
	}()
	return out
}

// Mapear aplica f sequencialmente a cada item de entrada, preservando a ordem.
func Mapear[T, R any](ctx context.Context, in <-chan T, f func(T) R) <-chan R {
	return Distribuir(ctx, in, 1, f)
}

// Distribuir (fan-out) processa a entrada com n workers e junta os resultados
// em um único channel (fan-in). A ordem de saída não é garantida quando n > 1.
func Distribuir[T, R any](ctx context.Context, in <-chan T, n int, f func(T) R) <-chan R {
	n = max(1, n)
	canais := make([]<-chan R, n)
	for i := range canais {
		saida := make(chan R)
		canais[i] = saida
		go func() {
			defer close(saida)
			for v := range in {
				select {
				case saida <- f(v):
				case <-ctx.Done():
					return
				}
			}
		}()
	}
	return Mesclar(ctx, canais...)
}

// Mesclar (fan-in) combina vários channels em um só, que é fechado quando
// todos os de entrada terminam (ou ctx é cancelado).
func Mesclar[T any](ctx context.Context, canais ...<-chan T) <-chan T {
	out := make(chan T)
	var wg sync.WaitGroup
	wg.Add(len(canais))
	for _, c := range canais {
		go func() {
			defer wg.Done()
			for v := range c {
				select {
				case out <- v:
				case <-ctx.Done():
					return
				}
			}
		}()
	}
	go func() {
		wg.Wait()
		close(out)
	}()
	return out
}

// Coletar lê o channel até o fim (ou cancelamento) e devolve os itens.
func Coletar[T any](ctx context.Context, in <-chan T) []T {
	r := []T{}
	for {
		select {
		case v, ok := <-in:
			if !ok {
				return r
			}
			r = append(r, v)
		case <-ctx.Done():
			return r
		}
	}
}
