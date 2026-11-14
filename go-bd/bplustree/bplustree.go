// Pacote bplustree implementa uma B+tree em memória: os valores ficam só nas
// folhas, que são encadeadas para permitir varredura por intervalo.
package bplustree

import (
	"cmp"
	"errors"
	"fmt"
	"sort"
)

// ErrOrdemInvalida é retornado quando a ordem é menor que 3.
var ErrOrdemInvalida = errors.New("bplustree: ordem deve ser >= 3")

type no[K cmp.Ordered, V any] struct {
	chaves []K
	vals   []V         // só em folhas
	filhos []*no[K, V] // só em nós internos: len(chaves)+1
	prox   *no[K, V]   // próxima folha
}

func (n *no[K, V]) folha() bool { return n.filhos == nil }

// Arvore guarda no máximo m chaves por nó; nós não-raiz têm ao menos m/2.
type Arvore[K cmp.Ordered, V any] struct {
	m    int
	raiz *no[K, V]
	n    int
}

// Nova cria uma árvore com ordem m (máximo de chaves por nó, m >= 3).
func Nova[K cmp.Ordered, V any](m int) (*Arvore[K, V], error) {
	if m < 3 {
		return nil, ErrOrdemInvalida
	}
	return &Arvore[K, V]{m: m, raiz: &no[K, V]{}}, nil
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

// indiceFilho escolhe o filho para a chave k (separador = menor chave do filho à direita).
func (n *no[K, V]) indiceFilho(k K) int {
	return sort.Search(len(n.chaves), func(j int) bool { return k < n.chaves[j] })
}

func (n *no[K, V]) indiceFolha(k K) (int, bool) {
	i := sort.Search(len(n.chaves), func(j int) bool { return n.chaves[j] >= k })
	return i, i < len(n.chaves) && n.chaves[i] == k
}

func (a *Arvore[K, V]) acharFolha(k K) *no[K, V] {
	n := a.raiz
	for !n.folha() {
		n = n.filhos[n.indiceFilho(k)]
	}
	return n
}

// Buscar procura a chave.
func (a *Arvore[K, V]) Buscar(k K) (V, bool) {
	f := a.acharFolha(k)
	if i, ok := f.indiceFolha(k); ok {
		return f.vals[i], true
	}
	var z V
	return z, false
}

// Inserir grava k=v e devolve true se a chave era nova.
func (a *Arvore[K, V]) Inserir(k K, v V) bool {
	sep, novo, dividiu, nova := a.inserir(a.raiz, k, v)
	if dividiu {
		a.raiz = &no[K, V]{chaves: []K{sep}, filhos: []*no[K, V]{a.raiz, novo}}
	}
	if nova {
		a.n++
	}
	return nova
}

func (a *Arvore[K, V]) inserir(n *no[K, V], k K, v V) (sep K, direito *no[K, V], dividiu, nova bool) {
	if n.folha() {
		i, achou := n.indiceFolha(k)
		if achou {
			n.vals[i] = v
			return sep, nil, false, false
		}
		n.chaves = inserirEm(n.chaves, i, k)
		n.vals = inserirEm(n.vals, i, v)
		if len(n.chaves) <= a.m {
			return sep, nil, false, true
		}
		meio := (a.m + 1) / 2
		d := &no[K, V]{prox: n.prox}
		d.chaves = append(d.chaves, n.chaves[meio:]...)
		d.vals = append(d.vals, n.vals[meio:]...)
		limpar(n.chaves, meio)
		limpar(n.vals, meio)
		n.chaves, n.vals = n.chaves[:meio], n.vals[:meio]
		n.prox = d
		return d.chaves[0], d, true, true
	}
	i := n.indiceFilho(k)
	s, d, div, nova := a.inserir(n.filhos[i], k, v)
	if !div {
		return sep, nil, false, nova
	}
	n.chaves = inserirEm(n.chaves, i, s)
	n.filhos = inserirEm(n.filhos, i+1, d)
	if len(n.chaves) <= a.m {
		return sep, nil, false, nova
	}
	meio := (a.m + 1) / 2
	sobe := n.chaves[meio]
	dir := &no[K, V]{}
	dir.chaves = append(dir.chaves, n.chaves[meio+1:]...)
	dir.filhos = append(dir.filhos, n.filhos[meio+1:]...)
	limpar(n.chaves, meio)
	limpar(n.filhos, meio+1)
	n.chaves = n.chaves[:meio]
	n.filhos = n.filhos[:meio+1]
	return sobe, dir, true, nova
}

// limpar zera s[de:] para não reter referências após o corte.
func limpar[T any](s []T, de int) {
	var z T
	for i := de; i < len(s); i++ {
		s[i] = z
	}
}

// Remover apaga a chave; devolve true se existia.
func (a *Arvore[K, V]) Remover(k K) bool {
	ok := a.remover(a.raiz, k)
	if !a.raiz.folha() && len(a.raiz.chaves) == 0 {
		a.raiz = a.raiz.filhos[0]
	}
	if ok {
		a.n--
	}
	return ok
}

func (a *Arvore[K, V]) min() int { return a.m / 2 }

func (a *Arvore[K, V]) remover(n *no[K, V], k K) bool {
	if n.folha() {
		i, achou := n.indiceFolha(k)
		if !achou {
			return false
		}
		n.chaves = removerDe(n.chaves, i)
		n.vals = removerDe(n.vals, i)
		return true
	}
	i := n.indiceFilho(k)
	ok := a.remover(n.filhos[i], k)
	if ok && len(n.filhos[i].chaves) < a.min() {
		a.rebalancear(n, i)
	}
	return ok
}

func (a *Arvore[K, V]) rebalancear(pai *no[K, V], i int) {
	c := pai.filhos[i]
	min := a.min()
	if i > 0 && len(pai.filhos[i-1].chaves) > min {
		e := pai.filhos[i-1]
		u := len(e.chaves) - 1
		if c.folha() {
			c.chaves = inserirEm(c.chaves, 0, e.chaves[u])
			c.vals = inserirEm(c.vals, 0, e.vals[u])
			e.chaves, e.vals = removerDe(e.chaves, u), removerDe(e.vals, u)
			pai.chaves[i-1] = c.chaves[0]
		} else {
			c.chaves = inserirEm(c.chaves, 0, pai.chaves[i-1])
			c.filhos = inserirEm(c.filhos, 0, e.filhos[len(e.filhos)-1])
			pai.chaves[i-1] = e.chaves[u]
			e.chaves = removerDe(e.chaves, u)
			e.filhos = removerDe(e.filhos, len(e.filhos)-1)
		}
		return
	}
	if i < len(pai.filhos)-1 && len(pai.filhos[i+1].chaves) > min {
		d := pai.filhos[i+1]
		if c.folha() {
			c.chaves = append(c.chaves, d.chaves[0])
			c.vals = append(c.vals, d.vals[0])
			d.chaves, d.vals = removerDe(d.chaves, 0), removerDe(d.vals, 0)
			pai.chaves[i] = d.chaves[0]
		} else {
			c.chaves = append(c.chaves, pai.chaves[i])
			c.filhos = append(c.filhos, d.filhos[0])
			pai.chaves[i] = d.chaves[0]
			d.chaves = removerDe(d.chaves, 0)
			d.filhos = removerDe(d.filhos, 0)
		}
		return
	}
	if i > 0 {
		a.mesclar(pai, i-1)
	} else {
		a.mesclar(pai, i)
	}
}

// mesclar junta filhos[j+1] em filhos[j] e remove o separador j do pai.
func (a *Arvore[K, V]) mesclar(pai *no[K, V], j int) {
	e, d := pai.filhos[j], pai.filhos[j+1]
	if e.folha() {
		e.chaves = append(e.chaves, d.chaves...)
		e.vals = append(e.vals, d.vals...)
		e.prox = d.prox
	} else {
		e.chaves = append(e.chaves, pai.chaves[j])
		e.chaves = append(e.chaves, d.chaves...)
		e.filhos = append(e.filhos, d.filhos...)
	}
	pai.chaves = removerDe(pai.chaves, j)
	pai.filhos = removerDe(pai.filhos, j+1)
}

// Intervalo visita, em ordem, as chaves em [de, ate). Para se fn devolver false.
func (a *Arvore[K, V]) Intervalo(de, ate K, fn func(K, V) bool) {
	f := a.acharFolha(de)
	i, _ := f.indiceFolha(de)
	for f != nil {
		for ; i < len(f.chaves); i++ {
			if f.chaves[i] >= ate {
				return
			}
			if !fn(f.chaves[i], f.vals[i]) {
				return
			}
		}
		f, i = f.prox, 0
	}
}

// Percorrer visita todas as chaves em ordem.
func (a *Arvore[K, V]) Percorrer(fn func(K, V) bool) {
	f := a.raiz
	for !f.folha() {
		f = f.filhos[0]
	}
	for ; f != nil; f = f.prox {
		for i := range f.chaves {
			if !fn(f.chaves[i], f.vals[i]) {
				return
			}
		}
	}
}

// Altura devolve o número de níveis.
func (a *Arvore[K, V]) Altura() int {
	h := 1
	for n := a.raiz; !n.folha(); n = n.filhos[0] {
		h++
	}
	return h
}

// Validar confere os invariantes: ocupação, ordenação, separadores,
// profundidade uniforme e encadeamento das folhas.
func (a *Arvore[K, V]) Validar() error {
	prof := -1
	var folhas []*no[K, V]
	var rec func(n *no[K, V], nivel int, raiz bool, lo, hi *K) error
	rec = func(n *no[K, V], nivel int, raiz bool, lo, hi *K) error {
		if len(n.chaves) > a.m {
			return fmt.Errorf("nó com %d chaves (máx %d)", len(n.chaves), a.m)
		}
		if !raiz && len(n.chaves) < a.min() {
			return fmt.Errorf("nó com %d chaves (mín %d)", len(n.chaves), a.min())
		}
		for i := range n.chaves {
			if i > 0 && n.chaves[i-1] >= n.chaves[i] {
				return errors.New("chaves fora de ordem")
			}
			if lo != nil && n.chaves[i] < *lo {
				return errors.New("chave abaixo do limite inferior")
			}
			if hi != nil && n.chaves[i] >= *hi {
				return errors.New("chave acima do limite superior")
			}
		}
		if n.folha() {
			if len(n.vals) != len(n.chaves) {
				return errors.New("folha com valores inconsistentes")
			}
			if prof == -1 {
				prof = nivel
			} else if prof != nivel {
				return errors.New("folhas em profundidades diferentes")
			}
			folhas = append(folhas, n)
			return nil
		}
		if len(n.filhos) != len(n.chaves)+1 {
			return errors.New("número de filhos inconsistente")
		}
		for i, f := range n.filhos {
			l, h := lo, hi
			if i > 0 {
				l = &n.chaves[i-1]
			}
			if i < len(n.chaves) {
				h = &n.chaves[i]
			}
			if err := rec(f, nivel+1, false, l, h); err != nil {
				return err
			}
		}
		return nil
	}
	if err := rec(a.raiz, 0, true, nil, nil); err != nil {
		return err
	}
	total := 0
	for i, f := range folhas {
		total += len(f.chaves)
		if i+1 < len(folhas) && f.prox != folhas[i+1] {
			return errors.New("encadeamento de folhas quebrado")
		}
		if i+1 == len(folhas) && f.prox != nil {
			return errors.New("última folha com próxima")
		}
	}
	if total != a.n {
		return fmt.Errorf("contagem %d difere de n=%d", total, a.n)
	}
	return nil
}
