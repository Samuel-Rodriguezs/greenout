// Pacote trie implementa uma árvore de prefixos para strings.
package trie

import "sort"

type no struct {
	filhos map[rune]*no
	fim    bool
}

func novoNo() *no { return &no{filhos: map[rune]*no{}} }

// Trie guarda um conjunto de palavras.
type Trie struct {
	raiz *no
	qtd  int
}

// Nova cria uma trie vazia.
func Nova() *Trie { return &Trie{raiz: novoNo()} }

// Tamanho devolve a quantidade de palavras distintas.
func (t *Trie) Tamanho() int { return t.qtd }

// Inserir adiciona a palavra; devolve false se já existia.
func (t *Trie) Inserir(palavra string) bool {
	n := t.raiz
	for _, r := range palavra {
		f, ok := n.filhos[r]
		if !ok {
			f = novoNo()
			n.filhos[r] = f
		}
		n = f
	}
	if n.fim {
		return false
	}
	n.fim = true
	t.qtd++
	return true
}

func (t *Trie) achar(prefixo string) *no {
	n := t.raiz
	for _, r := range prefixo {
		f, ok := n.filhos[r]
		if !ok {
			return nil
		}
		n = f
	}
	return n
}

// Contem informa se a palavra exata foi inserida.
func (t *Trie) Contem(palavra string) bool {
	n := t.achar(palavra)
	return n != nil && n.fim
}

// TemPrefixo informa se alguma palavra começa com prefixo.
func (t *Trie) TemPrefixo(prefixo string) bool { return t.achar(prefixo) != nil }

// ComPrefixo devolve, em ordem alfabética, as palavras que começam com prefixo.
func (t *Trie) ComPrefixo(prefixo string) []string {
	n := t.achar(prefixo)
	if n == nil {
		return nil
	}
	var res []string
	var desce func(n *no, atual []rune)
	desce = func(n *no, atual []rune) {
		if n.fim {
			res = append(res, string(atual))
		}
		for r, f := range n.filhos {
			desce(f, append(atual[:len(atual):len(atual)], r))
		}
	}
	desce(n, []rune(prefixo))
	sort.Strings(res)
	return res
}

// Remover apaga a palavra e poda ramos vazios; devolve false se não existia.
func (t *Trie) Remover(palavra string) bool {
	if !t.Contem(palavra) {
		return false
	}
	runas := []rune(palavra)
	caminho := make([]*no, 0, len(runas)+1)
	n := t.raiz
	caminho = append(caminho, n)
	for _, r := range runas {
		n = n.filhos[r]
		caminho = append(caminho, n)
	}
	n.fim = false
	t.qtd--
	for i := len(runas); i > 0; i-- {
		if caminho[i].fim || len(caminho[i].filhos) > 0 {
			break
		}
		delete(caminho[i-1].filhos, runas[i-1])
	}
	return true
}
