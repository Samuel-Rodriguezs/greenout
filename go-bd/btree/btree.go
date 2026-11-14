// Pacote btree implementa uma B-tree em memória (estilo CLRS) com grau
// mínimo t: todo nó, exceto a raiz, guarda entre t-1 e 2t-1 chaves.
package btree

import (
	"cmp"
	"errors"
	"fmt"
	"sort"
)

// ErrGrauInvalido é retornado quando o grau mínimo é menor que 2.
var ErrGrauInvalido = errors.New("btree: grau mínimo deve ser >= 2")

type no[K cmp.Ordered, V any] struct {
	chaves []K
	vals   []V
	filhos []*no[K, V]
}

func (n *no[K, V]) folha() bool { return len(n.filhos) == 0 }

// busca devolve o primeiro índice i tal que chaves[i] >= k e se há igualdade.
func (n *no[K, V]) busca(k K) (int, bool) {
	i := sort.Search(len(n.chaves), func(j int) bool { return n.chaves[j] >= k })
	return i, i < len(n.chaves) && n.chaves[i] == k
}

// Arvore é uma B-tree ordenada por K.
type Arvore[K cmp.Ordered, V any] struct {
	t    int
	raiz *no[K, V]
	n    int
}

// Nova cria uma árvore com grau mínimo t (t >= 2).
func Nova[K cmp.Ordered, V any](t int) (*Arvore[K, V], error) {
	if t < 2 {
		return nil, ErrGrauInvalido
	}
	return &Arvore[K, V]{t: t, raiz: &no[K, V]{}}, nil
}

// Tamanho devolve a quantidade de chaves.
func (a *Arvore[K, V]) Tamanho() int { return a.n }

func inserirEm[T any](s []T, i int, x T) []T {
	var z T
	s = append(s, z)
	copy(s[i+1:], s[i:])
	s[i] = x
	return s
}

func removerDe[T any](s []T, i int) []T {
	copy(s[i:], s[i+1:])
	var z T
	s[len(s)-1] = z
	return s[:len(s)-1]
}

// Buscar procura a chave.
func (a *Arvore[K, V]) Buscar(k K) (V, bool) {
	n := a.raiz
	for {
		i, achou := n.busca(k)
		if achou {
			return n.vals[i], true
		}
		if n.folha() {
			var z V
			return z, false
		}
		n = n.filhos[i]
	}
}

// Inserir grava k=v; devolve true se a chave era nova.
func (a *Arvore[K, V]) Inserir(k K, v V) bool {
	if len(a.raiz.chaves) == 2*a.t-1 {
		antiga := a.raiz
		a.raiz = &no[K, V]{filhos: []*no[K, V]{antiga}}
		a.dividir(a.raiz, 0)
	}
	novo := a.inserirNaoCheio(a.raiz, k, v)
	if novo {
		a.n++
	}
	return novo
}

func (a *Arvore[K, V]) dividir(pai *no[K, V], i int) {
	t := a.t
	y := pai.filhos[i]
	z := &no[K, V]{}
	medK, medV := y.chaves[t-1], y.vals[t-1]
	z.chaves = append(z.chaves, y.chaves[t:]...)
	z.vals = append(z.vals, y.vals[t:]...)
	if !y.folha() {
		z.filhos = append(z.filhos, y.filhos[t:]...)
		for j := t; j < len(y.filhos); j++ {
			y.filhos[j] = nil
		}
		y.filhos = y.filhos[:t]
	}
	y.chaves = y.chaves[:t-1]
	y.vals = y.vals[:t-1]
	pai.chaves = inserirEm(pai.chaves, i, medK)
	pai.vals = inserirEm(pai.vals, i, medV)
	pai.filhos = inserirEm(pai.filhos, i+1, z)
}

func (a *Arvore[K, V]) inserirNaoCheio(n *no[K, V], k K, v V) bool {
	for {
		i, achou := n.busca(k)
		if achou {
			n.vals[i] = v
			return false
		}
		if n.folha() {
			n.chaves = inserirEm(n.chaves, i, k)
			n.vals = inserirEm(n.vals, i, v)
			return true
		}
		if len(n.filhos[i].chaves) == 2*a.t-1 {
			a.dividir(n, i)
			if k == n.chaves[i] {
				n.vals[i] = v
				return false
			}
			if k > n.chaves[i] {
				i++
			}
		}
		n = n.filhos[i]
	}
}

// Remover apaga a chave; devolve true se ela existia.
func (a *Arvore[K, V]) Remover(k K) bool {
	ok := a.remover(a.raiz, k)
	if len(a.raiz.chaves) == 0 && !a.raiz.folha() {
		a.raiz = a.raiz.filhos[0]
	}
	if ok {
		a.n--
	}
	return ok
}

func (a *Arvore[K, V]) remover(x *no[K, V], k K) bool {
	t := a.t
	i, achou := x.busca(k)
	if achou {
		if x.folha() {
			x.chaves = removerDe(x.chaves, i)
			x.vals = removerDe(x.vals, i)
			return true
		}
		if len(x.filhos[i].chaves) >= t {
			pk, pv := maximo(x.filhos[i])
			x.chaves[i], x.vals[i] = pk, pv
			return a.remover(x.filhos[i], pk)
		}
		if len(x.filhos[i+1].chaves) >= t {
			sk, sv := minimo(x.filhos[i+1])
			x.chaves[i], x.vals[i] = sk, sv
			return a.remover(x.filhos[i+1], sk)
		}
		a.fundir(x, i)
		return a.remover(x.filhos[i], k)
	}
	if x.folha() {
		return false
	}
	if len(x.filhos[i].chaves) < t {
		i = a.garantir(x, i)
	}
	return a.remover(x.filhos[i], k)
}

func maximo[K cmp.Ordered, V any](n *no[K, V]) (K, V) {
	for !n.folha() {
		n = n.filhos[len(n.filhos)-1]
	}
	u := len(n.chaves) - 1
	return n.chaves[u], n.vals[u]
}

func minimo[K cmp.Ordered, V any](n *no[K, V]) (K, V) {
	for !n.folha() {
		n = n.filhos[0]
	}
	return n.chaves[0], n.vals[0]
}

// fundir junta filhos[i], a chave i do pai e filhos[i+1] em filhos[i].
func (a *Arvore[K, V]) fundir(x *no[K, V], i int) {
	e, d := x.filhos[i], x.filhos[i+1]
	e.chaves = append(e.chaves, x.chaves[i])
	e.vals = append(e.vals, x.vals[i])
	e.chaves = append(e.chaves, d.chaves...)
	e.vals = append(e.vals, d.vals...)
	e.filhos = append(e.filhos, d.filhos...)
	x.chaves = removerDe(x.chaves, i)
	x.vals = removerDe(x.vals, i)
	x.filhos = removerDe(x.filhos, i+1)
}

// garantir assegura que filhos[i] tenha ao menos t chaves antes de descer;
// devolve o índice do filho em que se deve continuar.
func (a *Arvore[K, V]) garantir(x *no[K, V], i int) int {
	t := a.t
	c := x.filhos[i]
	if i > 0 && len(x.filhos[i-1].chaves) >= t {
		e := x.filhos[i-1]
		u := len(e.chaves) - 1
		c.chaves = inserirEm(c.chaves, 0, x.chaves[i-1])
		c.vals = inserirEm(c.vals, 0, x.vals[i-1])
		x.chaves[i-1], x.vals[i-1] = e.chaves[u], e.vals[u]
		e.chaves, e.vals = e.chaves[:u], e.vals[:u]
		if !e.folha() {
			uf := len(e.filhos) - 1
			c.filhos = inserirEm(c.filhos, 0, e.filhos[uf])
			e.filhos[uf] = nil
			e.filhos = e.filhos[:uf]
		}
		return i
	}
	if i < len(x.filhos)-1 && len(x.filhos[i+1].chaves) >= t {
		d := x.filhos[i+1]
		c.chaves = append(c.chaves, x.chaves[i])
		c.vals = append(c.vals, x.vals[i])
		x.chaves[i], x.vals[i] = d.chaves[0], d.vals[0]
		d.chaves = removerDe(d.chaves, 0)
		d.vals = removerDe(d.vals, 0)
		if !d.folha() {
			c.filhos = append(c.filhos, d.filhos[0])
			d.filhos = removerDe(d.filhos, 0)
		}
		return i
	}
	if i < len(x.filhos)-1 {
		a.fundir(x, i)
		return i
	}
	a.fundir(x, i-1)
	return i - 1
}

// Percorrer visita as chaves em ordem crescente; para se fn devolver false.
func (a *Arvore[K, V]) Percorrer(fn func(K, V) bool) {
	percorrer(a.raiz, fn)
}

func percorrer[K cmp.Ordered, V any](n *no[K, V], fn func(K, V) bool) bool {
	for i := range n.chaves {
		if !n.folha() && !percorrer(n.filhos[i], fn) {
			return false
		}
		if !fn(n.chaves[i], n.vals[i]) {
			return false
		}
	}
	if !n.folha() {
		return percorrer(n.filhos[len(n.filhos)-1], fn)
	}
	return true
}

// Altura devolve o número de níveis (1 para uma árvore só com a raiz).
func (a *Arvore[K, V]) Altura() int {
	h := 1
	for n := a.raiz; !n.folha(); n = n.filhos[0] {
		h++
	}
	return h
}

// Validar confere os invariantes estruturais da árvore.
func (a *Arvore[K, V]) Validar() error {
	prof := -1
	contagem := 0
	var anterior *K
	var rec func(n *no[K, V], nivel int, raiz bool) error
	rec = func(n *no[K, V], nivel int, raiz bool) error {
		if len(n.chaves) != len(n.vals) {
			return errors.New("chaves e valores com tamanhos diferentes")
		}
		if len(n.chaves) > 2*a.t-1 {
			return fmt.Errorf("nó cheio demais: %d chaves", len(n.chaves))
		}
		if !raiz && len(n.chaves) < a.t-1 {
			return fmt.Errorf("nó com poucas chaves: %d", len(n.chaves))
		}
		if n.folha() {
			if prof == -1 {
				prof = nivel
			} else if prof != nivel {
				return errors.New("folhas em profundidades diferentes")
			}
		} else if len(n.filhos) != len(n.chaves)+1 {
			return errors.New("número de filhos inconsistente")
		}
		for i := range n.chaves {
			if !n.folha() {
				if err := rec(n.filhos[i], nivel+1, false); err != nil {
					return err
				}
			}
			if anterior != nil && n.chaves[i] <= *anterior {
				return errors.New("chaves fora de ordem")
			}
			k := n.chaves[i]
			anterior = &k
			contagem++
		}
		if !n.folha() {
			return rec(n.filhos[len(n.filhos)-1], nivel+1, false)
		}
		return nil
	}
	if err := rec(a.raiz, 0, true); err != nil {
		return err
	}
	if contagem != a.n {
		return fmt.Errorf("contagem %d difere de n=%d", contagem, a.n)
	}
	return nil
}
