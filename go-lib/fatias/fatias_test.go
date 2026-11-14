package fatias

import (
	"reflect"
	"strconv"
	"testing"
)

func TestMapear(t *testing.T) {
	casos := []struct {
		nome string
		in   []int
		want []string
	}{
		{"vazio", nil, []string{}},
		{"um", []int{1}, []string{"1"}},
		{"varios", []int{1, 2, 3}, []string{"1", "2", "3"}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := Mapear(c.in, strconv.Itoa); !reflect.DeepEqual(got, c.want) {
				t.Fatalf("got %v want %v", got, c.want)
			}
		})
	}
}

func TestFiltrar(t *testing.T) {
	par := func(n int) bool { return n%2 == 0 }
	casos := []struct {
		nome     string
		in, want []int
	}{
		{"vazio", nil, []int{}},
		{"nenhum", []int{1, 3}, []int{}},
		{"todos", []int{2, 4}, []int{2, 4}},
		{"misto", []int{1, 2, 3, 4}, []int{2, 4}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := Filtrar(c.in, par); !reflect.DeepEqual(got, c.want) {
				t.Fatalf("got %v want %v", got, c.want)
			}
		})
	}
}

func TestReduzir(t *testing.T) {
	soma := func(a, v int) int { return a + v }
	if got := Reduzir([]int{}, 7, soma); got != 7 {
		t.Fatalf("vazio: %d", got)
	}
	if got := Reduzir([]int{1, 2, 3, 4}, 0, soma); got != 10 {
		t.Fatalf("soma: %d", got)
	}
	if got := Reduzir([]string{"a", "b"}, "", func(a string, v string) string { return a + v }); got != "ab" {
		t.Fatalf("concat: %q", got)
	}
}

func TestAgruparPor(t *testing.T) {
	got := AgruparPor([]string{"ab", "c", "de", "f", "ghi"}, func(s string) int { return len(s) })
	want := map[int][]string{1: {"c", "f"}, 2: {"ab", "de"}, 3: {"ghi"}}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("got %v", got)
	}
	if len(AgruparPor([]int(nil), func(i int) int { return i })) != 0 {
		t.Fatal("esperava mapa vazio")
	}
}

func TestParticionar(t *testing.T) {
	casos := []struct {
		nome string
		in   []int
		n    int
		want [][]int
	}{
		{"exato", []int{1, 2, 3, 4}, 2, [][]int{{1, 2}, {3, 4}}},
		{"resto", []int{1, 2, 3, 4, 5}, 2, [][]int{{1, 2}, {3, 4}, {5}}},
		{"maior que len", []int{1, 2}, 5, [][]int{{1, 2}}},
		{"vazio", nil, 3, [][]int{}},
		{"zero", []int{1}, 0, nil},
		{"negativo", []int{1}, -1, nil},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := Particionar(c.in, c.n); !reflect.DeepEqual(got, c.want) {
				t.Fatalf("got %v want %v", got, c.want)
			}
		})
	}
	orig := []int{1, 2, 3}
	p := Particionar(orig, 2)
	p[0][0] = 99
	if orig[0] != 1 {
		t.Fatal("blocos não devem compartilhar memória")
	}
}

func TestUnicos(t *testing.T) {
	casos := []struct {
		nome     string
		in, want []int
	}{
		{"vazio", nil, []int{}},
		{"sem dup", []int{1, 2}, []int{1, 2}},
		{"dups", []int{3, 1, 3, 2, 1}, []int{3, 1, 2}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := Unicos(c.in); !reflect.DeepEqual(got, c.want) {
				t.Fatalf("got %v", got)
			}
		})
	}
}
