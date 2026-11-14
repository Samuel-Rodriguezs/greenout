package pool

import (
	"bytes"
	"sync"
	"testing"
)

func novoBuffers(max int) *Pool[*bytes.Buffer] {
	return Novo(max, func() *bytes.Buffer { return new(bytes.Buffer) }, func(b *bytes.Buffer) { b.Reset() })
}

func TestReuso(t *testing.T) {
	p := novoBuffers(2)
	b := p.Obter()
	b.WriteString("sujo")
	if !p.Devolver(b) {
		t.Fatal("deveria reter")
	}
	b2 := p.Obter()
	if b2 != b {
		t.Fatal("deveria reaproveitar o mesmo objeto")
	}
	if b2.Len() != 0 {
		t.Fatal("objeto deveria ter sido resetado")
	}
	criados, reusados := p.Estatisticas()
	if criados != 1 || reusados != 1 {
		t.Fatalf("criados=%d reusados=%d", criados, reusados)
	}
}

func TestLimite(t *testing.T) {
	casos := []struct {
		nome     string
		max      int
		devolver int
		retidos  int
	}{
		{"cabe tudo", 3, 3, 3},
		{"excede", 2, 4, 2},
		{"max zero descarta", 0, 2, 0},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			p := novoBuffers(c.max)
			var bs []*bytes.Buffer
			for i := 0; i < c.devolver; i++ {
				bs = append(bs, p.Obter())
			}
			for _, b := range bs {
				p.Devolver(b)
			}
			if p.Ociosos() != c.retidos {
				t.Fatalf("ociosos %d", p.Ociosos())
			}
		})
	}
}

func TestSemResetar(t *testing.T) {
	p := Novo(1, func() *int { return new(int) }, nil)
	x := p.Obter()
	*x = 5
	p.Devolver(x)
	if y := p.Obter(); *y != 5 {
		t.Fatal("sem reset o valor deveria persistir")
	}
}

func TestCriarObrigatorio(t *testing.T) {
	defer func() {
		if recover() == nil {
			t.Fatal("esperava panic")
		}
	}()
	Novo[int](1, nil, nil)
}

func TestConcorrencia(t *testing.T) {
	p := novoBuffers(4)
	var wg sync.WaitGroup
	for g := 0; g < 16; g++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for i := 0; i < 500; i++ {
				b := p.Obter()
				b.WriteString("x")
				p.Devolver(b)
			}
		}()
	}
	wg.Wait()
	if p.Ociosos() > 4 {
		t.Fatalf("ociosos %d acima do limite", p.Ociosos())
	}
}
