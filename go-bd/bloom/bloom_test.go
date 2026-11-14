package bloom

import (
	"fmt"
	"sync"
	"testing"
)

func TestParametrosInvalidos(t *testing.T) {
	casos := []struct {
		n int
		p float64
	}{{0, 0.01}, {-5, 0.01}, {10, 0}, {10, 1}, {10, -0.5}, {10, 1.5}}
	for _, c := range casos {
		if _, err := Novo(c.n, c.p); err != ErrParametros {
			t.Errorf("Novo(%d,%v): err = %v", c.n, c.p, err)
		}
	}
}

func TestSemFalsosNegativosETaxa(t *testing.T) {
	casos := []struct {
		n   int
		p   float64
		max float64 // taxa máxima tolerada na medição
	}{
		{100, 0.05, 0.12},
		{1000, 0.01, 0.025},
		{5000, 0.001, 0.006},
	}
	for _, c := range casos {
		t.Run(fmt.Sprintf("n=%d p=%v", c.n, c.p), func(t *testing.T) {
			f, err := Novo(c.n, c.p)
			if err != nil {
				t.Fatal(err)
			}
			for i := 0; i < c.n; i++ {
				f.Adicionar([]byte(fmt.Sprintf("in-%d", i)))
			}
			for i := 0; i < c.n; i++ {
				if !f.Possui([]byte(fmt.Sprintf("in-%d", i))) {
					t.Fatalf("falso negativo em in-%d", i)
				}
			}
			const sondas = 20000
			falsos := 0
			for i := 0; i < sondas; i++ {
				if f.Possui([]byte(fmt.Sprintf("fora-%d", i))) {
					falsos++
				}
			}
			if taxa := float64(falsos) / sondas; taxa > c.max {
				t.Fatalf("taxa de falso positivo %.4f > %.4f", taxa, c.max)
			}
			if est := f.TaxaEstimada(); est > 3*c.p {
				t.Fatalf("taxa estimada %.4f muito alta", est)
			}
			if f.Adicionados() != uint64(c.n) {
				t.Fatalf("adicionados = %d", f.Adicionados())
			}
		})
	}
}

func TestVazioENulo(t *testing.T) {
	f, _ := Novo(10, 0.01)
	if f.Possui([]byte("x")) {
		t.Fatal("filtro vazio não pode conter nada")
	}
	f.Adicionar(nil)
	f.Adicionar([]byte{})
	if !f.Possui(nil) || !f.Possui([]byte{}) {
		t.Fatal("elemento vazio deveria ser encontrado")
	}
}

func TestSerializacaoIdaEVolta(t *testing.T) {
	f, _ := Novo(500, 0.01)
	for i := 0; i < 500; i++ {
		f.Adicionar([]byte(fmt.Sprint("k", i)))
	}
	b, err := f.MarshalBinary()
	if err != nil {
		t.Fatal(err)
	}
	g, err := Carregar(b)
	if err != nil {
		t.Fatal(err)
	}
	for i := 0; i < 500; i++ {
		if !g.Possui([]byte(fmt.Sprint("k", i))) {
			t.Fatalf("k%d perdido na serialização", i)
		}
	}
	if g.m != f.m || g.k != f.k || g.Adicionados() != 500 {
		t.Fatal("parâmetros divergem")
	}
}

func TestCarregarInvalido(t *testing.T) {
	f, _ := Novo(50, 0.01)
	f.Adicionar([]byte("a"))
	bom, _ := f.MarshalBinary()

	casos := []struct {
		nome string
		b    func() []byte
	}{
		{"nil", func() []byte { return nil }},
		{"curto", func() []byte { return bom[:10] }},
		{"truncado", func() []byte { return bom[:len(bom)-5] }},
		{"magic errado", func() []byte { b := append([]byte(nil), bom...); b[0] ^= 1; return b }},
		{"bit invertido", func() []byte { b := append([]byte(nil), bom...); b[tamCabecalho+2] ^= 4; return b }},
		{"crc invertido", func() []byte { b := append([]byte(nil), bom...); b[len(b)-1] ^= 1; return b }},
		{"sobrando", func() []byte { return append(append([]byte(nil), bom...), 0) }},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if _, err := Carregar(c.b()); err != ErrFormato {
				t.Fatalf("err = %v", err)
			}
		})
	}
}

func TestUniao(t *testing.T) {
	a, _ := Novo(100, 0.01)
	b, _ := Novo(100, 0.01)
	c, _ := Novo(200, 0.01)
	a.Adicionar([]byte("so-a"))
	b.Adicionar([]byte("so-b"))
	if err := a.Uniao(b); err != nil {
		t.Fatal(err)
	}
	if !a.Possui([]byte("so-a")) || !a.Possui([]byte("so-b")) {
		t.Fatal("união deveria conter ambos")
	}
	if b.Possui([]byte("so-a")) {
		t.Fatal("o filtro de origem não deveria mudar")
	}
	if err := a.Uniao(c); err != ErrIncompativel {
		t.Fatalf("err = %v", err)
	}
	if err := a.Uniao(a); err != nil {
		t.Fatalf("união consigo mesmo: %v", err)
	}
}

func TestConcorrencia(t *testing.T) {
	f, _ := Novo(10000, 0.01)
	var wg sync.WaitGroup
	for g := 0; g < 8; g++ {
		wg.Add(1)
		go func(g int) {
			defer wg.Done()
			for i := 0; i < 500; i++ {
				k := []byte(fmt.Sprintf("g%d-%d", g, i))
				f.Adicionar(k)
				if !f.Possui(k) {
					t.Errorf("falso negativo %s", k)
				}
			}
		}(g)
	}
	wg.Wait()
	if f.Adicionados() != 4000 {
		t.Fatalf("adicionados = %d", f.Adicionados())
	}
}
