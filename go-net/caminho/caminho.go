// Pacote caminho calcula caminhos de menor custo em uma topologia de rede
// (grafo ponderado) com o algoritmo de Dijkstra, como num protocolo de
// roteamento link-state (OSPF/IS-IS).
package caminho

import (
	"container/heap"
	"errors"
	"fmt"
	"sort"
)

// Erros conhecidos.
var (
	ErrNoDesconhecido = errors.New("caminho: nó desconhecido")
	ErrSemCaminho     = errors.New("caminho: destino inalcançável")
	ErrCustoNegativo  = errors.New("caminho: custo de enlace negativo")
)

type aresta struct {
	para  string
	custo int
}

// Topologia é um grafo de roteadores com enlaces ponderados.
type Topologia struct {
	adj map[string][]aresta
}

// Nova cria uma topologia vazia.
func Nova() *Topologia { return &Topologia{adj: map[string][]aresta{}} }

// AdicionarNo registra um roteador sem enlaces.
func (t *Topologia) AdicionarNo(n string) {
	if _, ok := t.adj[n]; !ok {
		t.adj[n] = nil
	}
}

// AdicionarEnlace cria um enlace bidirecional com o custo dado. Custos devem
// ser não negativos (Dijkstra não os admite negativos).
func (t *Topologia) AdicionarEnlace(a, b string, custo int) error {
	if err := t.AdicionarEnlaceDirecionado(a, b, custo); err != nil {
		return err
	}
	return t.AdicionarEnlaceDirecionado(b, a, custo)
}

// AdicionarEnlaceDirecionado cria um enlace de a para b apenas.
func (t *Topologia) AdicionarEnlaceDirecionado(a, b string, custo int) error {
	if custo < 0 {
		return fmt.Errorf("%w: %s->%s = %d", ErrCustoNegativo, a, b, custo)
	}
	t.AdicionarNo(a)
	t.AdicionarNo(b)
	t.adj[a] = append(t.adj[a], aresta{b, custo})
	return nil
}

// RemoverEnlace apaga os enlaces entre a e b (nos dois sentidos) e informa se algum existia.
func (t *Topologia) RemoverEnlace(a, b string) bool {
	removeu := false
	filtra := func(de, para string) {
		out := t.adj[de][:0]
		for _, e := range t.adj[de] {
			if e.para == para {
				removeu = true
				continue
			}
			out = append(out, e)
		}
		t.adj[de] = out
	}
	filtra(a, b)
	filtra(b, a)
	return removeu
}

type item struct {
	no   string
	dist int
}

type fila []item

func (f fila) Len() int { return len(f) }
func (f fila) Less(i, j int) bool {
	if f[i].dist != f[j].dist {
		return f[i].dist < f[j].dist
	}
	return f[i].no < f[j].no // desempate determinístico
}
func (f fila) Swap(i, j int) { f[i], f[j] = f[j], f[i] }
func (f *fila) Push(x any)   { *f = append(*f, x.(item)) }
func (f *fila) Pop() any {
	v := (*f)[len(*f)-1]
	*f = (*f)[:len(*f)-1]
	return v
}

// Arvore é o resultado de Dijkstra a partir de uma origem.
type Arvore struct {
	Origem string
	Dist   map[string]int    // custo mínimo até cada nó alcançável
	Pai    map[string]string // predecessor no caminho mínimo
}

// MenoresCaminhos executa Dijkstra a partir de origem. Entre caminhos de mesmo
// custo, prefere o predecessor de menor nome, tornando o resultado determinístico.
func (t *Topologia) MenoresCaminhos(origem string) (*Arvore, error) {
	if _, ok := t.adj[origem]; !ok {
		return nil, fmt.Errorf("%w: %q", ErrNoDesconhecido, origem)
	}
	arv := &Arvore{Origem: origem, Dist: map[string]int{origem: 0}, Pai: map[string]string{}}
	feito := map[string]bool{}
	f := &fila{{origem, 0}}
	for f.Len() > 0 {
		cur := heap.Pop(f).(item)
		if feito[cur.no] {
			continue
		}
		feito[cur.no] = true
		for _, e := range t.adj[cur.no] {
			if feito[e.para] {
				continue
			}
			nd := cur.dist + e.custo
			antigo, visto := arv.Dist[e.para]
			if !visto || nd < antigo || (nd == antigo && cur.no < arv.Pai[e.para]) {
				arv.Dist[e.para] = nd
				arv.Pai[e.para] = cur.no
				if !visto || nd < antigo {
					heap.Push(f, item{e.para, nd})
				}
			}
		}
	}
	return arv, nil
}

// Caminho reconstrói o caminho da origem até destino e seu custo total.
func (a *Arvore) Caminho(destino string) ([]string, int, error) {
	d, ok := a.Dist[destino]
	if !ok {
		return nil, 0, fmt.Errorf("%w: %q", ErrSemCaminho, destino)
	}
	var rev []string
	for n := destino; ; n = a.Pai[n] {
		rev = append(rev, n)
		if n == a.Origem {
			break
		}
	}
	for i, j := 0, len(rev)-1; i < j; i, j = i+1, j-1 {
		rev[i], rev[j] = rev[j], rev[i]
	}
	return rev, d, nil
}

// CaminhoMinimo é um atalho para MenoresCaminhos(origem).Caminho(destino).
func (t *Topologia) CaminhoMinimo(origem, destino string) ([]string, int, error) {
	if _, ok := t.adj[destino]; !ok {
		return nil, 0, fmt.Errorf("%w: %q", ErrNoDesconhecido, destino)
	}
	arv, err := t.MenoresCaminhos(origem)
	if err != nil {
		return nil, 0, err
	}
	return arv.Caminho(destino)
}

// ProximoSalto devolve, para cada destino alcançável, o primeiro roteador
// depois da origem no caminho mínimo: o conteúdo da tabela de roteamento da origem.
func (a *Arvore) ProximoSalto() map[string]string {
	out := map[string]string{}
	for dest := range a.Dist {
		if dest == a.Origem {
			continue
		}
		n := dest
		for a.Pai[n] != a.Origem {
			n = a.Pai[n]
		}
		out[dest] = n
	}
	return out
}

// Nos devolve os nomes de todos os roteadores em ordem alfabética.
func (t *Topologia) Nos() []string {
	out := make([]string, 0, len(t.adj))
	for n := range t.adj {
		out = append(out, n)
	}
	sort.Strings(out)
	return out
}
