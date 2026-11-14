package lab

import (
	"reflect"
	"testing"
)

func montarArvore(vals ...int) *ArvoreBusca[int] {
	a := &ArvoreBusca[int]{}
	for _, v := range vals {
		a.Inserir(v)
	}
	return a
}

func TestArvoreBuscaInserirContem(t *testing.T) {
	a := &ArvoreBusca[int]{}
	if a.Contem(1) || a.Altura() != 0 || a.Tamanho() != 0 || len(a.EmOrdem()) != 0 {
		t.Fatal("árvore vazia inconsistente")
	}
	a = montarArvore(5, 3, 8, 1, 4, 7, 9)
	if !a.Inserir(6) || a.Inserir(6) {
		t.Fatal("duplicado deve devolver false")
	}
	if a.Tamanho() != 8 {
		t.Fatalf("tamanho = %d", a.Tamanho())
	}
	if !a.Contem(4) || a.Contem(100) {
		t.Fatal("Contem incorreto")
	}
	if got := a.EmOrdem(); !reflect.DeepEqual(got, []int{1, 3, 4, 5, 6, 7, 8, 9}) {
		t.Fatalf("got %v", got)
	}
	if a.Altura() != 4 {
		t.Fatalf("altura = %d", a.Altura())
	}
}

func TestArvoreBuscaRemover(t *testing.T) {
	casos := []struct {
		nome string
		rem  int
		want []int
	}{
		{"folha", 1, []int{3, 4, 5, 7, 8, 9}},
		{"um filho", 9, []int{1, 3, 4, 5, 7, 8}},
		{"dois filhos", 3, []int{1, 4, 5, 7, 8, 9}},
		{"raiz", 5, []int{1, 3, 4, 7, 8, 9}},
		{"ausente", 42, []int{1, 3, 4, 5, 7, 8, 9}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			a := montarArvore(5, 3, 8, 1, 4, 7, 9)
			ok := a.Remover(c.rem)
			if ok != (c.rem != 42) {
				t.Fatalf("Remover devolveu %v", ok)
			}
			if got := a.EmOrdem(); !reflect.DeepEqual(got, c.want) {
				t.Fatalf("got %v want %v", got, c.want)
			}
			if a.Tamanho() != len(c.want) {
				t.Fatalf("tamanho = %d", a.Tamanho())
			}
		})
	}
	a := montarArvore(1)
	a.Remover(1)
	if a.Tamanho() != 0 || a.Contem(1) {
		t.Fatal("deveria esvaziar")
	}
}
