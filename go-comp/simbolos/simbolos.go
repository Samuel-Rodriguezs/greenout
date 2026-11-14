// Pacote simbolos implementa a tabela de símbolos com escopos aninhados.
//
// Existem três níveis fixos: o escopo "universo" (embutidos), o escopo
// global do programa e os escopos locais (blocos e funções) empilhados
// por Entrar/Sair.
package simbolos

import (
	"fmt"

	"greenout/comp/token"
)

// Categoria classifica um símbolo.
type Categoria int

const (
	Variavel Categoria = iota
	Funcao
	Parametro
	Embutido
)

func (c Categoria) String() string {
	switch c {
	case Variavel:
		return "variável"
	case Funcao:
		return "função"
	case Parametro:
		return "parâmetro"
	case Embutido:
		return "embutido"
	}
	return fmt.Sprintf("Categoria(%d)", int(c))
}

// Simbolo descreve um nome declarado.
type Simbolo struct {
	Nome         string
	Categoria    Categoria
	Pos          token.Posicao
	Profundidade int  // 0 = global, -1 = universo, >0 = locais
	Indice       int  // ordem de declaração dentro do escopo
	Usado        bool // lido ao menos uma vez
	Dado         any  // informação das fases seguintes (ex.: tipo)
}

// Escopo é um nível da tabela.
type Escopo struct {
	Pai          *Escopo
	Funcao       bool // verdadeiro se é o escopo de uma função
	Profundidade int
	porNome      map[string]*Simbolo
	ordem        []*Simbolo
}

func novoEscopo(pai *Escopo, funcao bool, prof int) *Escopo {
	return &Escopo{Pai: pai, Funcao: funcao, Profundidade: prof, porNome: map[string]*Simbolo{}}
}

// Simbolos devolve os símbolos do escopo na ordem de declaração.
func (e *Escopo) Simbolos() []*Simbolo { return e.ordem }

// Buscar procura o nome apenas neste escopo.
func (e *Escopo) Buscar(nome string) (*Simbolo, bool) {
	s, ok := e.porNome[nome]
	return s, ok
}

// NaoUsados devolve as variáveis declaradas neste escopo e nunca lidas.
func (e *Escopo) NaoUsados() []*Simbolo {
	var res []*Simbolo
	for _, s := range e.ordem {
		if s.Categoria == Variavel && !s.Usado {
			res = append(res, s)
		}
	}
	return res
}

// Tabela é a pilha de escopos.
type Tabela struct {
	universo *Escopo
	global   *Escopo
	atual    *Escopo
}

// Nova cria uma tabela com escopos universo e global; o escopo atual é o global.
func Nova() *Tabela {
	u := novoEscopo(nil, false, -1)
	g := novoEscopo(u, false, 0)
	return &Tabela{universo: u, global: g, atual: g}
}

// Atual devolve o escopo corrente.
func (t *Tabela) Atual() *Escopo { return t.atual }

// Global devolve o escopo global.
func (t *Tabela) Global() *Escopo { return t.global }

// Profundidade devolve a profundidade do escopo corrente (0 no global).
func (t *Tabela) Profundidade() int { return t.atual.Profundidade }

// Entrar abre um novo escopo local; funcao indica que é o corpo de uma função.
func (t *Tabela) Entrar(funcao bool) *Escopo {
	t.atual = novoEscopo(t.atual, funcao, t.atual.Profundidade+1)
	return t.atual
}

// Sair fecha o escopo corrente e o devolve. No escopo global não faz nada
// e devolve nil.
func (t *Tabela) Sair() *Escopo {
	if t.atual == t.global {
		return nil
	}
	s := t.atual
	t.atual = s.Pai
	return s
}

// DentroDeFuncao informa se algum escopo ativo é de função.
func (t *Tabela) DentroDeFuncao() bool {
	for e := t.atual; e != nil; e = e.Pai {
		if e.Funcao {
			return true
		}
	}
	return false
}

func declarar(e *Escopo, nome string, cat Categoria, pos token.Posicao) (*Simbolo, error) {
	if ant, ok := e.porNome[nome]; ok {
		return ant, fmt.Errorf("'%s' já declarado neste escopo", nome)
	}
	s := &Simbolo{Nome: nome, Categoria: cat, Pos: pos, Profundidade: e.Profundidade, Indice: len(e.ordem)}
	e.porNome[nome] = s
	e.ordem = append(e.ordem, s)
	return s, nil
}

// Declarar registra um nome no escopo corrente. Se já existir no mesmo
// escopo devolve o símbolo anterior e um erro.
func (t *Tabela) Declarar(nome string, cat Categoria, pos token.Posicao) (*Simbolo, error) {
	return declarar(t.atual, nome, cat, pos)
}

// DeclararEmbutido registra um nome no escopo universo, visível em todo o programa.
func (t *Tabela) DeclararEmbutido(nome string, dado any) *Simbolo {
	s, err := declarar(t.universo, nome, Embutido, token.Posicao{})
	if err != nil {
		return s
	}
	s.Dado = dado
	s.Usado = true
	return s
}

// Resolver procura o nome do escopo corrente para fora.
func (t *Tabela) Resolver(nome string) (*Simbolo, bool) {
	for e := t.atual; e != nil; e = e.Pai {
		if s, ok := e.porNome[nome]; ok {
			return s, true
		}
	}
	return nil, false
}

// ResolverLocal procura o nome apenas no escopo corrente.
func (t *Tabela) ResolverLocal(nome string) (*Simbolo, bool) {
	return t.atual.Buscar(nome)
}
