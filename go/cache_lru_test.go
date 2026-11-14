package lab

import (
	"reflect"
	"testing"
)

func TestCacheLRU(t *testing.T) {
	c := NovoCacheLRU[string, int](2)
	if _, ok := c.Obter("a"); ok {
		t.Fatal("cache vazio")
	}
	c.Colocar("a", 1)
	c.Colocar("b", 2)
	if v, ok := c.Obter("a"); !ok || v != 1 { // "a" vira a mais recente
		t.Fatalf("got %d,%v", v, ok)
	}
	c.Colocar("c", 3) // expulsa "b"
	if _, ok := c.Obter("b"); ok {
		t.Fatal("b deveria ter sido expulso")
	}
	if !reflect.DeepEqual(c.Chaves(), []string{"c", "a"}) {
		t.Fatalf("chaves = %v", c.Chaves())
	}
	c.Colocar("a", 10) // atualiza sem crescer
	if v, _ := c.Obter("a"); v != 10 || c.Tamanho() != 2 {
		t.Fatalf("v=%d tamanho=%d", v, c.Tamanho())
	}
	c.Colocar("d", 4) // expulsa "c"
	if !reflect.DeepEqual(c.Chaves(), []string{"d", "a"}) {
		t.Fatalf("chaves = %v", c.Chaves())
	}
}

func TestCacheLRUCapacidadeMinima(t *testing.T) {
	c := NovoCacheLRU[int, string](0)
	c.Colocar(1, "x")
	c.Colocar(2, "y")
	if c.Tamanho() != 1 {
		t.Fatalf("tamanho = %d", c.Tamanho())
	}
	if _, ok := c.Obter(1); ok {
		t.Fatal("1 deveria ter sido expulso")
	}
	if v, ok := c.Obter(2); !ok || v != "y" {
		t.Fatalf("got %q,%v", v, ok)
	}
}
