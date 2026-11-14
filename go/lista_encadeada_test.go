package lab

import (
	"reflect"
	"testing"
)

func TestListaEncadeada(t *testing.T) {
	var l ListaEncadeada[int]
	if got := l.ParaSlice(); len(got) != 0 {
		t.Fatalf("lista vazia: %v", got)
	}
	l.Inverter() // vazia não deve quebrar
	l.Adicionar(2)
	l.Adicionar(3)
	l.AdicionarInicio(1)
	if got := l.ParaSlice(); !reflect.DeepEqual(got, []int{1, 2, 3}) {
		t.Fatalf("got %v", got)
	}
	if v, err := l.Obter(2); err != nil || v != 3 {
		t.Fatalf("Obter(2) = %d, %v", v, err)
	}
	for _, i := range []int{-1, 3} {
		if _, err := l.Obter(i); err != ErrListaIndiceInvalido {
			t.Fatalf("Obter(%d) err = %v", i, err)
		}
		if _, err := l.Remover(i); err != ErrListaIndiceInvalido {
			t.Fatalf("Remover(%d) err = %v", i, err)
		}
	}
	l.Inverter()
	if got := l.ParaSlice(); !reflect.DeepEqual(got, []int{3, 2, 1}) {
		t.Fatalf("invertida: %v", got)
	}
	l.Adicionar(0) // cauda deve ser a antiga cabeça (1)
	if got := l.ParaSlice(); !reflect.DeepEqual(got, []int{3, 2, 1, 0}) {
		t.Fatalf("após inverter+adicionar: %v", got)
	}
}

func TestListaEncadeadaRemover(t *testing.T) {
	var l ListaEncadeada[string]
	for _, s := range []string{"a", "b", "c", "d"} {
		l.Adicionar(s)
	}
	if v, _ := l.Remover(0); v != "a" {
		t.Fatalf("removeu %q", v)
	}
	if v, _ := l.Remover(2); v != "d" { // cauda
		t.Fatalf("removeu %q", v)
	}
	l.Adicionar("e")
	if got := l.ParaSlice(); !reflect.DeepEqual(got, []string{"b", "c", "e"}) {
		t.Fatalf("got %v", got)
	}
	l.Remover(0)
	l.Remover(0)
	l.Remover(0)
	if l.Tamanho() != 0 {
		t.Fatalf("tamanho = %d", l.Tamanho())
	}
	l.Adicionar("z")
	if got := l.ParaSlice(); !reflect.DeepEqual(got, []string{"z"}) {
		t.Fatalf("got %v", got)
	}
}
