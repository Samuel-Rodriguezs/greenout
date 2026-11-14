package dijkstra

import (
	"reflect"
	"testing"
)

func TestMenoresCaminhos(t *testing.T) {
	g := [][]Aresta{
		0: {{1, 7}, {2, 9}, {5, 14}},
		1: {{0, 7}, {2, 10}, {3, 15}},
		2: {{0, 9}, {1, 10}, {3, 11}, {5, 2}},
		3: {{1, 15}, {2, 11}, {4, 6}},
		4: {{3, 6}, {5, 9}},
		5: {{0, 14}, {2, 2}, {4, 9}},
		6: {},
	}
	dist, pai := MenoresCaminhos(g, 0)
	esperado := []int{0, 7, 9, 20, 20, 11, Inf}
	if !reflect.DeepEqual(dist, esperado) {
		t.Fatalf("dist=%v, esperado %v", dist, esperado)
	}
	if c := Caminho(dist, pai, 4); !reflect.DeepEqual(c, []int{0, 2, 5, 4}) {
		t.Errorf("caminho=%v", c)
	}
	if c := Caminho(dist, pai, 6); c != nil {
		t.Errorf("esperado nil, veio %v", c)
	}
	if c := Caminho(dist, pai, 0); !reflect.DeepEqual(c, []int{0}) {
		t.Errorf("caminho para origem=%v", c)
	}
}

func TestBordas(t *testing.T) {
	dist, _ := MenoresCaminhos(nil, 0)
	if len(dist) != 0 {
		t.Error("grafo vazio deveria dar dist vazio")
	}
	dist, _ = MenoresCaminhos([][]Aresta{{}}, 3)
	if dist[0] != Inf {
		t.Error("origem inválida deveria deixar tudo infinito")
	}
	dist, _ = MenoresCaminhos([][]Aresta{{{0, 5}}}, 0)
	if dist[0] != 0 {
		t.Error("laço não deve alterar origem")
	}
}

func BenchmarkGrade(b *testing.B) {
	n := 2000
	g := make([][]Aresta, n)
	for i := 0; i < n; i++ {
		g[i] = append(g[i], Aresta{(i + 1) % n, 1 + i%7}, Aresta{(i * 7) % n, 3})
	}
	for i := 0; i < b.N; i++ {
		MenoresCaminhos(g, 0)
	}
}
