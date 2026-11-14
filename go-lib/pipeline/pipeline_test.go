package pipeline

import (
	"context"
	"slices"
	"testing"
	"time"
)

func TestGerarMapearOrdem(t *testing.T) {
	ctx := context.Background()
	casos := []struct {
		nome string
		in   []int
		want []int
	}{
		{"vazio", nil, []int{}},
		{"varios", []int{1, 2, 3}, []int{2, 4, 6}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			got := Coletar(ctx, Mapear(ctx, Gerar(ctx, c.in...), func(n int) int { return n * 2 }))
			if !slices.Equal(got, c.want) {
				t.Fatalf("got %v", got)
			}
		})
	}
}

func TestDistribuir(t *testing.T) {
	ctx := context.Background()
	for _, workers := range []int{0, 1, 4, 16} {
		entrada := make([]int, 100)
		want := make([]int, 100)
		for i := range entrada {
			entrada[i] = i
			want[i] = i * i
		}
		got := Coletar(ctx, Distribuir(ctx, Gerar(ctx, entrada...), workers, func(n int) int { return n * n }))
		slices.Sort(got) // ordem não é garantida
		if !slices.Equal(got, want) {
			t.Fatalf("workers=%d resultado divergiu", workers)
		}
	}
}

func TestMesclar(t *testing.T) {
	ctx := context.Background()
	got := Coletar(ctx, Mesclar(ctx, Gerar(ctx, 1, 2), Gerar(ctx, 3), Gerar[int](ctx)))
	slices.Sort(got)
	if !slices.Equal(got, []int{1, 2, 3}) {
		t.Fatalf("got %v", got)
	}
	if got := Coletar(ctx, Mesclar[int](ctx)); len(got) != 0 {
		t.Fatalf("sem canais: %v", got)
	}
}

func TestCancelamentoNaoVazaGoroutines(t *testing.T) {
	ctx, cancela := context.WithCancel(context.Background())
	entrada := make([]int, 1000)
	saida := Distribuir(ctx, Gerar(ctx, entrada...), 4, func(n int) int { return n })
	<-saida // consome apenas um e cancela
	cancela()
	// o channel precisa fechar sem que ninguém mais o consuma
	fechou := make(chan struct{})
	go func() {
		for range saida {
		}
		close(fechou)
	}()
	select {
	case <-fechou:
	case <-time.After(2 * time.Second):
		t.Fatal("pipeline não encerrou após cancelamento")
	}
}

func TestColetarCancelado(t *testing.T) {
	ctx, cancela := context.WithCancel(context.Background())
	cancela()
	bloqueado := make(chan int) // nunca emite
	if got := Coletar(ctx, bloqueado); len(got) != 0 {
		t.Fatalf("got %v", got)
	}
}
