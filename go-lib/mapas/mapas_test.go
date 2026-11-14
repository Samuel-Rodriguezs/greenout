package mapas

import (
	"reflect"
	"testing"
)

func TestChavesValores(t *testing.T) {
	casos := []struct {
		nome string
		in   map[string]int
		ks   []string
		vs   []int
	}{
		{"nil", nil, []string{}, []int{}},
		{"um", map[string]int{"a": 1}, []string{"a"}, []int{1}},
		{"varios", map[string]int{"c": 3, "a": 1, "b": 2}, []string{"a", "b", "c"}, []int{1, 2, 3}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := Chaves(c.in); !reflect.DeepEqual(got, c.ks) {
				t.Fatalf("chaves %v", got)
			}
			if got := Valores(c.in); !reflect.DeepEqual(got, c.vs) {
				t.Fatalf("valores %v", got)
			}
		})
	}
}

func TestCopiar(t *testing.T) {
	o := map[string]int{"a": 1}
	c := Copiar(o)
	c["b"] = 2
	if len(o) != 1 || !reflect.DeepEqual(c, map[string]int{"a": 1, "b": 2}) {
		t.Fatal("cópia deve ser independente")
	}
	if got := Copiar[string, int](nil); got == nil || len(got) != 0 {
		t.Fatal("nil deve virar vazio não-nil")
	}
}

func TestMesclar(t *testing.T) {
	got := Mesclar(map[string]int{"a": 1, "b": 2}, nil, map[string]int{"b": 3, "c": 4})
	want := map[string]int{"a": 1, "b": 3, "c": 4}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("got %v", got)
	}
	if len(Mesclar[string, int]()) != 0 {
		t.Fatal("sem args deve ser vazio")
	}
}

func TestInverter(t *testing.T) {
	got := Inverter(map[string]int{"a": 1, "b": 2})
	if !reflect.DeepEqual(got, map[int]string{1: "a", 2: "b"}) {
		t.Fatalf("got %v", got)
	}
}

func TestFiltrarMapa(t *testing.T) {
	got := FiltrarMapa(map[string]int{"a": 1, "b": 2, "c": 3}, func(k string, v int) bool { return v > 1 && k != "c" })
	if !reflect.DeepEqual(got, map[string]int{"b": 2}) {
		t.Fatalf("got %v", got)
	}
}
