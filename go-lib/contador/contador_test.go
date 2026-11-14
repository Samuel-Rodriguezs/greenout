package contador

import (
	"fmt"
	"reflect"
	"sync"
	"testing"
)

func TestContadorSequencial(t *testing.T) {
	casos := []struct {
		nome   string
		frags  int
		deltas []int64
		total  int64
	}{
		{"vazio", 4, nil, 0},
		{"soma simples", 4, []int64{1, 2, 3}, 6},
		{"negativos", 3, []int64{10, -4, -6}, 0},
		{"fragmentos invalidos usam padrao", 0, []int64{5, 5}, 10},
		{"um fragmento", 1, []int64{1, 1, 1}, 3},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			ct := Novo(c.frags)
			for _, d := range c.deltas {
				ct.Adicionar(d)
			}
			if got := ct.Total(); got != c.total {
				t.Fatalf("total %d", got)
			}
			ct.Zerar()
			if ct.Total() != 0 {
				t.Fatal("Zerar falhou")
			}
		})
	}
}

func TestContadorConcorrente(t *testing.T) {
	const gor, ops = 32, 1000
	ct := Novo(8)
	var wg sync.WaitGroup
	for g := 0; g < gor; g++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for i := 0; i < ops; i++ {
				ct.Incrementar()
			}
		}()
	}
	wg.Wait()
	if got := ct.Total(); got != gor*ops {
		t.Fatalf("total %d", got)
	}
}

func TestPorChave(t *testing.T) {
	p := NovoPorChave(0)
	if p.Obter("x") != 0 {
		t.Fatal("inexistente deve ser 0")
	}
	if got := p.Adicionar("a", 2); got != 2 {
		t.Fatalf("got %d", got)
	}
	p.Adicionar("a", 3)
	p.Adicionar("b", -1)
	if p.Obter("a") != 5 || p.Obter("b") != -1 {
		t.Fatal("valores errados")
	}
	if got := p.Instantaneo(); !reflect.DeepEqual(got, map[string]int64{"a": 5, "b": -1}) {
		t.Fatalf("instantâneo %v", got)
	}
}

func TestPorChaveConcorrente(t *testing.T) {
	p := NovoPorChave(4)
	var wg sync.WaitGroup
	for g := 0; g < 16; g++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for i := 0; i < 500; i++ {
				p.Adicionar(fmt.Sprintf("k%d", i%10), 1)
			}
		}()
	}
	wg.Wait()
	snap := p.Instantaneo()
	if len(snap) != 10 {
		t.Fatalf("chaves %d", len(snap))
	}
	for k, v := range snap {
		if v != 16*50 {
			t.Fatalf("%s=%d", k, v)
		}
	}
}
