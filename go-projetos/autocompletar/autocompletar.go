// Pacote autocompletar implementa sugestões por prefixo usando uma trie,
// com ranking por frequência de uso.
package autocompletar

import (
	"sort"
	"strings"
)

type no struct {
	filhos map[rune]*no
	fim    bool
	peso   int
}

// Trie guarda palavras e seus pesos (frequência).
type Trie struct {
	raiz *no
	n    int
}

// Nova cria uma trie vazia.
func Nova() *Trie { return &Trie{raiz: &no{filhos: map[rune]*no{}}} }

func normalizar(s string) string { return strings.ToLower(strings.TrimSpace(s)) }

// Inserir adiciona a palavra somando peso à frequência. Palavras vazias são ignoradas.
func (t *Trie) Inserir(palavra string, peso int) {
	palavra = normalizar(palavra)
	if palavra == "" {
		return
	}
	atual := t.raiz
	for _, r := range palavra {
		prox, ok := atual.filhos[r]
		if !ok {
			prox = &no{filhos: map[rune]*no{}}
			atual.filhos[r] = prox
		}
		atual = prox
	}
	if !atual.fim {
		atual.fim = true
		t.n++
	}
	atual.peso += peso
}

// Tamanho devolve a quantidade de palavras distintas.
func (t *Trie) Tamanho() int { return t.n }

func (t *Trie) buscar(prefixo string) *no {
	atual := t.raiz
	for _, r := range prefixo {
		atual = atual.filhos[r]
		if atual == nil {
			return nil
		}
	}
	return atual
}

// Contem informa se a palavra exata foi inserida.
func (t *Trie) Contem(palavra string) bool {
	n := t.buscar(normalizar(palavra))
	return n != nil && n.fim
}

type sugestao struct {
	palavra string
	peso    int
}

func coletar(n *no, prefixo []rune, saida *[]sugestao) {
	if n.fim {
		*saida = append(*saida, sugestao{string(prefixo), n.peso})
	}
	for r, f := range n.filhos {
		coletar(f, append(prefixo, r), saida)
	}
}

// Sugerir devolve até limite palavras com o prefixo, da maior para a menor
// frequência (empates em ordem alfabética). limite <= 0 devolve todas.
func (t *Trie) Sugerir(prefixo string, limite int) []string {
	prefixo = normalizar(prefixo)
	n := t.buscar(prefixo)
	if n == nil {
		return nil
	}
	var todas []sugestao
	coletar(n, []rune(prefixo), &todas)
	sort.Slice(todas, func(i, j int) bool {
		if todas[i].peso != todas[j].peso {
			return todas[i].peso > todas[j].peso
		}
		return todas[i].palavra < todas[j].palavra
	})
	if limite > 0 && len(todas) > limite {
		todas = todas[:limite]
	}
	r := make([]string, len(todas))
	for i, s := range todas {
		r[i] = s.palavra
	}
	return r
}
