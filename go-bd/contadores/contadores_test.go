package contadores

import (
	"fmt"
	"reflect"
	"sync"
	"testing"
)

func TestContador(t *testing.T) {
	casos := []struct {
		nome   string
		passos func(c *Contador)
		quer   int64
	}{
		{"zero", func(c *Contador) {}, 0},
		{"incrementar", func(c *Contador) { c.Incrementar(5); c.Incrementar(2) }, 7},
		{"decrementar abaixo de zero", func(c *Contador) { c.Decrementar(3) }, -3},
		{"misto", func(c *Contador) { c.Incrementar(10); c.Decrementar(4); c.Incrementar(1) }, 7},
		{"maximo sobe", func(c *Contador) { c.Incrementar(3); c.Maximo(10) }, 10},
		{"maximo nao desce", func(c *Contador) { c.Incrementar(10); c.Maximo(3) }, 10},
		{"incremento negativo", func(c *Contador) { c.Incrementar(-4) }, -4},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			var ct Contador
			c.passos(&ct)
			if ct.Valor() != c.quer {
				t.Fatalf("valor = %d, quer %d", ct.Valor(), c.quer)
			}
		})
	}
}

func TestZerarDevolveAnterior(t *testing.T) {
	var c Contador
	c.Incrementar(9)
	if ant := c.Zerar(); ant != 9 || c.Valor() != 0 {
		t.Fatalf("anterior=%d valor=%d", ant, c.Valor())
	}
}

func TestConjunto(t *testing.T) {
	s := NovoConjunto()
	if s.Valor("x") != 0 || len(s.Nomes()) != 0 {
		t.Fatal("leitura não deve criar contador")
	}
	s.Incrementar("leituras", 3)
	s.Incrementar("leituras", 2)
	s.Incrementar("escritas", 1)
	if s.Valor("leituras") != 5 {
		t.Fatalf("leituras = %d", s.Valor("leituras"))
	}
	if got := s.Nomes(); !reflect.DeepEqual(got, []string{"escritas", "leituras"}) {
		t.Fatalf("nomes = %v", got)
	}
	foto := s.Instantaneo()
	s.Incrementar("leituras", 100)
	if foto["leituras"] != 5 {
		t.Fatal("instantâneo deveria ser uma cópia")
	}
	if v, ok := s.Remover("escritas"); !ok || v != 1 {
		t.Fatalf("remover = %d %v", v, ok)
	}
	if _, ok := s.Remover("escritas"); ok {
		t.Fatal("remover duas vezes")
	}
	if s.Valor("escritas") != 0 {
		t.Fatal("removido deveria valer 0")
	}
}

func TestConcorrencia(t *testing.T) {
	s := NovoConjunto()
	var wg sync.WaitGroup
	const gs, n = 16, 1000
	for g := 0; g < gs; g++ {
		wg.Add(1)
		go func(g int) {
			defer wg.Done()
			for i := 0; i < n; i++ {
				s.Incrementar("total", 1)
				s.Incrementar(fmt.Sprint("g", g%4), 1)
				s.Valor("total")
			}
		}(g)
	}
	wg.Wait()
	if s.Valor("total") != gs*n {
		t.Fatalf("total = %d", s.Valor("total"))
	}
	soma := int64(0)
	for _, nome := range []string{"g0", "g1", "g2", "g3"} {
		soma += s.Valor(nome)
	}
	if soma != gs*n {
		t.Fatalf("soma dos grupos = %d", soma)
	}
}

func TestMaximoConcorrente(t *testing.T) {
	var c Contador
	var wg sync.WaitGroup
	for g := 0; g < 32; g++ {
		wg.Add(1)
		go func(g int) {
			defer wg.Done()
			for i := 0; i < 500; i++ {
				c.Maximo(int64(g*1000 + i))
			}
		}(g)
	}
	wg.Wait()
	if c.Valor() != 31*1000+499 {
		t.Fatalf("máximo = %d", c.Valor())
	}
}
