package lab

import (
	"reflect"
	"sync"
	"testing"
)

func TestContadorSeguroBasico(t *testing.T) {
	c := NovoContadorSeguro()
	if c.Valor("x") != 0 || c.Total() != 0 {
		t.Fatal("deveria iniciar zerado")
	}
	if got := c.Incrementar("x", 2); got != 2 {
		t.Fatalf("got %d", got)
	}
	c.Incrementar("x", -5)
	c.Incrementar("y", 1)
	if c.Valor("x") != -3 || c.Total() != -2 {
		t.Fatalf("x=%d total=%d", c.Valor("x"), c.Total())
	}
	cp := c.Copia()
	cp["x"] = 100
	if c.Valor("x") != -3 {
		t.Fatal("cópia não deve afetar o original")
	}
	if !reflect.DeepEqual(c.Copia(), map[string]int{"x": -3, "y": 1}) {
		t.Fatalf("copia = %v", c.Copia())
	}
}

func TestContadorSeguroConcorrente(t *testing.T) {
	c := NovoContadorSeguro()
	var wg sync.WaitGroup
	for g := 0; g < 50; g++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for i := 0; i < 200; i++ {
				c.Incrementar("a", 1)
				c.Incrementar("b", 2)
			}
		}()
	}
	wg.Wait()
	if c.Valor("a") != 10000 || c.Valor("b") != 20000 || c.Total() != 30000 {
		t.Fatalf("a=%d b=%d", c.Valor("a"), c.Valor("b"))
	}
}
