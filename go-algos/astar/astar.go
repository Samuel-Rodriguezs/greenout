// Pacote astar implementa busca A* em grade com movimentos em 4 direções.
package astar

import "container/heap"

// Ponto é uma célula da grade.
type Ponto struct{ L, C int }

type no struct {
	p    Ponto
	f, g int
}

type fila []no

func (f fila) Len() int { return len(f) }
func (f fila) Less(i, j int) bool {
	if f[i].f != f[j].f {
		return f[i].f < f[j].f
	}
	return f[i].g > f[j].g
}
func (f fila) Swap(i, j int) { f[i], f[j] = f[j], f[i] }
func (f *fila) Push(x any)   { *f = append(*f, x.(no)) }
func (f *fila) Pop() any {
	v := *f
	x := v[len(v)-1]
	*f = v[:len(v)-1]
	return x
}

func abs(x int) int {
	if x < 0 {
		return -x
	}
	return x
}

// heuristica é a distância de Manhattan, admissível para 4 direções.
func heuristica(a, b Ponto) int { return abs(a.L-b.L) + abs(a.C-b.C) }

// Buscar procura o menor caminho de ini a fim. Células '#' são obstáculos.
// Devolve o caminho (inclusive extremos) ou ok=false se não existir.
func Buscar(grade []string, ini, fim Ponto) (caminho []Ponto, ok bool) {
	livre := func(p Ponto) bool {
		return p.L >= 0 && p.L < len(grade) && p.C >= 0 && p.C < len(grade[p.L]) && grade[p.L][p.C] != '#'
	}
	if !livre(ini) || !livre(fim) {
		return nil, false
	}
	g := map[Ponto]int{ini: 0}
	pai := map[Ponto]Ponto{}
	f := &fila{{ini, heuristica(ini, fim), 0}}
	for f.Len() > 0 {
		cur := heap.Pop(f).(no)
		if cur.g > g[cur.p] {
			continue
		}
		if cur.p == fim {
			for p := fim; p != ini; p = pai[p] {
				caminho = append(caminho, p)
			}
			caminho = append(caminho, ini)
			for i, j := 0, len(caminho)-1; i < j; i, j = i+1, j-1 {
				caminho[i], caminho[j] = caminho[j], caminho[i]
			}
			return caminho, true
		}
		for _, d := range [4]Ponto{{-1, 0}, {1, 0}, {0, -1}, {0, 1}} {
			v := Ponto{cur.p.L + d.L, cur.p.C + d.C}
			if !livre(v) {
				continue
			}
			ng := cur.g + 1
			if old, existe := g[v]; !existe || ng < old {
				g[v] = ng
				pai[v] = cur.p
				heap.Push(f, no{v, ng + heuristica(v, fim), ng})
			}
		}
	}
	return nil, false
}
