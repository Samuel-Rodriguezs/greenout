package bellmanford

import (
	"errors"
	"reflect"
	"testing"
)

func TestBellmanFord(t *testing.T) {
	casos := []struct {
		nome    string
		n       int
		arestas []Aresta
		origem  int
		dist    []int
		err     error
	}{
		{"pesos negativos", 5, []Aresta{{0, 1, 6}, {0, 2, 7}, {1, 2, 8}, {1, 3, 5}, {1, 4, -4}, {2, 3, -3}, {2, 4, 9}, {3, 1, -2}, {4, 0, 2}, {4, 3, 7}}, 0, []int{0, 2, 7, 4, -2}, nil},
		{"ciclo negativo", 3, []Aresta{{0, 1, 1}, {1, 2, -3}, {2, 1, 1}}, 0, nil, ErrCicloNegativo},
		{"ciclo negativo inalcançável", 4, []Aresta{{0, 1, 2}, {2, 3, -5}, {3, 2, 1}}, 0, []int{0, 2, Inf, Inf}, nil},
		{"vértice único", 1, nil, 0, []int{0}, nil},
		{"vazio", 0, nil, 0, []int{}, nil},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			dist, err := BellmanFord(c.n, c.arestas, c.origem)
			if !errors.Is(err, c.err) {
				t.Fatalf("erro=%v, esperado %v", err, c.err)
			}
			if err == nil && !reflect.DeepEqual(dist, c.dist) {
				t.Errorf("dist=%v, esperado %v", dist, c.dist)
			}
		})
	}
}
