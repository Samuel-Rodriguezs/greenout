package lista

import (
	"slices"
	"testing"
)

func de(vs ...int) *Lista[int] {
	l := &Lista[int]{}
	for _, v := range vs {
		l.AdicionarFim(v)
	}
	return l
}

func TestAdicionar(t *testing.T) {
	l := &Lista[int]{}
	l.AdicionarFim(2)
	l.AdicionarInicio(1)
	l.AdicionarFim(3)
	if got := l.Itens(); !slices.Equal(got, []int{1, 2, 3}) || l.Tamanho() != 3 {
		t.Fatalf("got %v", got)
	}
	vazia := &Lista[int]{}
	vazia.AdicionarInicio(7)
	if v, _ := vazia.RemoverUltimo(); v != 7 {
		t.Fatal("lista de um elemento")
	}
}

func TestRemocoes(t *testing.T) {
	casos := []struct {
		nome string
		in   []int
		op   func(l *Lista[int])
		want []int
	}{
		{"primeiro", []int{1, 2, 3}, func(l *Lista[int]) { l.RemoverPrimeiro() }, []int{2, 3}},
		{"ultimo", []int{1, 2, 3}, func(l *Lista[int]) { l.RemoverUltimo() }, []int{1, 2}},
		{"unico primeiro", []int{1}, func(l *Lista[int]) { l.RemoverPrimeiro() }, []int{}},
		{"unico ultimo", []int{1}, func(l *Lista[int]) { l.RemoverUltimo() }, []int{}},
		{"meio", []int{1, 2, 3}, func(l *Lista[int]) { l.RemoverSe(func(v int) bool { return v == 2 }) }, []int{1, 3}},
		{"cabeca por predicado", []int{1, 2, 3}, func(l *Lista[int]) { l.RemoverSe(func(v int) bool { return v == 1 }) }, []int{2, 3}},
		{"cauda por predicado", []int{1, 2, 3}, func(l *Lista[int]) { l.RemoverSe(func(v int) bool { return v == 3 }) }, []int{1, 2}},
		{"inexistente", []int{1, 2}, func(l *Lista[int]) { l.RemoverSe(func(v int) bool { return v == 9 }) }, []int{1, 2}},
		{"so primeira ocorrencia", []int{2, 2}, func(l *Lista[int]) { l.RemoverSe(func(v int) bool { return v == 2 }) }, []int{2}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			l := de(c.in...)
			c.op(l)
			if got := l.Itens(); !slices.Equal(got, c.want) || l.Tamanho() != len(c.want) {
				t.Fatalf("got %v tam %d", got, l.Tamanho())
			}
			// consistência dos ponteiros: remover tudo pelo fim
			n := 0
			for {
				if _, ok := l.RemoverUltimo(); !ok {
					break
				}
				n++
			}
			if n != len(c.want) {
				t.Fatalf("ligações inconsistentes: %d vs %d", n, len(c.want))
			}
		})
	}
}

func TestVazia(t *testing.T) {
	l := &Lista[string]{}
	if _, ok := l.RemoverPrimeiro(); ok {
		t.Fatal("primeiro")
	}
	if _, ok := l.RemoverUltimo(); ok {
		t.Fatal("ultimo")
	}
	if _, ok := l.Buscar(func(string) bool { return true }); ok {
		t.Fatal("buscar")
	}
	l.Inverter() // não deve falhar
	if len(l.Itens()) != 0 {
		t.Fatal("itens")
	}
}

func TestBuscar(t *testing.T) {
	l := de(1, 2, 3, 4)
	if v, ok := l.Buscar(func(v int) bool { return v > 2 }); !ok || v != 3 {
		t.Fatalf("got %d", v)
	}
	if _, ok := l.Buscar(func(v int) bool { return v > 10 }); ok {
		t.Fatal("não deveria achar")
	}
}

func TestInverter(t *testing.T) {
	casos := [][]int{{}, {1}, {1, 2}, {1, 2, 3, 4}}
	for _, in := range casos {
		l := de(in...)
		l.Inverter()
		want := slices.Clone(in)
		slices.Reverse(want)
		if got := l.Itens(); !slices.Equal(got, want) {
			t.Fatalf("got %v want %v", got, want)
		}
		// o ponteiro "ante" também precisa estar correto
		var volta []int
		for n := l.fim; n != nil; n = n.ante {
			volta = append(volta, n.valor)
		}
		slices.Reverse(volta)
		if len(in) > 0 && !slices.Equal(volta, want) {
			t.Fatalf("ante inconsistente: %v", volta)
		}
	}
}
