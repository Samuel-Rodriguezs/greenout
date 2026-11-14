package arvore

import (
	"cmp"
	"math/rand"
	"slices"
	"testing"
)

func nova(vs ...int) *Arvore[int] {
	a := Nova(cmp.Compare[int])
	for _, v := range vs {
		a.Inserir(v)
	}
	return a
}

func TestInserirBuscar(t *testing.T) {
	a := nova(5, 3, 8, 1, 4)
	if a.Tamanho() != 5 {
		t.Fatalf("tamanho %d", a.Tamanho())
	}
	if a.Inserir(3) || a.Tamanho() != 5 {
		t.Fatal("duplicado deve ser rejeitado")
	}
	if v, ok := a.Buscar(4); !ok || v != 4 {
		t.Fatal("buscar existente")
	}
	if _, ok := a.Buscar(99); ok {
		t.Fatal("buscar inexistente")
	}
	if got := a.EmOrdem(); !slices.Equal(got, []int{1, 3, 4, 5, 8}) {
		t.Fatalf("em ordem %v", got)
	}
}

func TestVazia(t *testing.T) {
	a := nova()
	if _, ok := a.Minimo(); ok {
		t.Fatal("min")
	}
	if _, ok := a.Maximo(); ok {
		t.Fatal("max")
	}
	if a.Altura() != 0 || a.Remover(1) || len(a.EmOrdem()) != 0 {
		t.Fatal("vazia")
	}
}

func TestMinMaxAltura(t *testing.T) {
	casos := []struct {
		nome        string
		in          []int
		min, max, h int
	}{
		{"um", []int{4}, 4, 4, 1},
		{"balanceada", []int{4, 2, 6, 1, 3, 5, 7}, 1, 7, 3},
		{"degenerada", []int{1, 2, 3, 4}, 1, 4, 4},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			a := nova(c.in...)
			mn, _ := a.Minimo()
			mx, _ := a.Maximo()
			if mn != c.min || mx != c.max || a.Altura() != c.h {
				t.Fatalf("min %d max %d h %d", mn, mx, a.Altura())
			}
		})
	}
}

func TestRemover(t *testing.T) {
	base := []int{50, 30, 70, 20, 40, 60, 80, 35, 45}
	casos := []struct {
		nome string
		rem  int
		ok   bool
	}{
		{"folha", 20, true},
		{"um filho", 30, true},
		{"dois filhos", 50, true},
		{"dois filhos subarvore", 40, true},
		{"raiz", 50, true},
		{"inexistente", 99, false},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			a := nova(base...)
			if got := a.Remover(c.rem); got != c.ok {
				t.Fatalf("Remover=%v", got)
			}
			want := slices.DeleteFunc(slices.Clone(base), func(v int) bool { return c.ok && v == c.rem })
			slices.Sort(want)
			if got := a.EmOrdem(); !slices.Equal(got, want) || a.Tamanho() != len(want) {
				t.Fatalf("got %v want %v", got, want)
			}
		})
	}
}

func TestRemoverAleatorio(t *testing.T) {
	r := rand.New(rand.NewSource(1))
	a := nova()
	ref := map[int]bool{}
	for i := 0; i < 2000; i++ {
		v := r.Intn(100)
		if r.Intn(2) == 0 {
			if a.Inserir(v) == ref[v] {
				t.Fatal("inserir divergiu")
			}
			ref[v] = true
		} else {
			if a.Remover(v) != ref[v] {
				t.Fatal("remover divergiu")
			}
			delete(ref, v)
		}
	}
	var want []int
	for v := range ref {
		want = append(want, v)
	}
	slices.Sort(want)
	if got := a.EmOrdem(); !slices.Equal(got, want) || a.Tamanho() != len(want) {
		t.Fatal("estado final divergiu")
	}
}
