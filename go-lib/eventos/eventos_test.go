package eventos

import (
	"slices"
	"sync"
	"sync/atomic"
	"testing"
)

type pedido struct {
	ID    int
	Valor float64
}

func TestPublicarSemAssinantes(t *testing.T) {
	var b Barramento[string]
	if n := b.Publicar("x"); n != 0 {
		t.Fatalf("n=%d", n)
	}
}

func TestOrdemEEntrega(t *testing.T) {
	var b Barramento[pedido]
	var log []string
	b.Inscrever(func(p pedido) { log = append(log, "a") })
	b.Inscrever(func(p pedido) { log = append(log, "b") })
	if n := b.Publicar(pedido{ID: 1}); n != 2 {
		t.Fatalf("n=%d", n)
	}
	if !slices.Equal(log, []string{"a", "b"}) {
		t.Fatalf("ordem %v", log)
	}
}

func TestCancelar(t *testing.T) {
	casos := []struct {
		nome     string
		cancelar int // índice a cancelar
		want     []int
	}{
		{"primeiro", 0, []int{1, 2}},
		{"meio", 1, []int{0, 2}},
		{"ultimo", 2, []int{0, 1}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			var b Barramento[int]
			var recebidos []int
			var cancelas []func()
			for i := 0; i < 3; i++ {
				cancelas = append(cancelas, b.Inscrever(func(int) { recebidos = append(recebidos, i) }))
			}
			cancelas[c.cancelar]()
			cancelas[c.cancelar]() // idempotente
			b.Publicar(0)
			if !slices.Equal(recebidos, c.want) || b.Assinantes() != 2 {
				t.Fatalf("recebidos %v assinantes %d", recebidos, b.Assinantes())
			}
		})
	}
}

func TestCancelarDentroDoTratador(t *testing.T) {
	var b Barramento[int]
	chamadas := 0
	var cancela func()
	cancela = b.Inscrever(func(int) { chamadas++; cancela() })
	b.Publicar(1)
	b.Publicar(2)
	if chamadas != 1 {
		t.Fatalf("chamadas=%d", chamadas)
	}
}

func TestConcorrencia(t *testing.T) {
	var b Barramento[int]
	var total atomic.Int64
	var wg sync.WaitGroup
	for g := 0; g < 8; g++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for i := 0; i < 100; i++ {
				cancela := b.Inscrever(func(n int) { total.Add(int64(n)) })
				b.Publicar(1)
				cancela()
			}
		}()
	}
	wg.Wait()
	if b.Assinantes() != 0 || total.Load() < 800 {
		t.Fatalf("assinantes=%d total=%d", b.Assinantes(), total.Load())
	}
}
