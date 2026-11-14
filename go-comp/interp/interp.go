// Pacote interp é um interpretador tree-walking para Mini, com ambientes
// encadeados e closures. Também define os valores de execução e as
// operações sobre eles, reaproveitados pela máquina virtual.
package interp

import (
	"errors"
	"fmt"

	"greenout/comp/ast"
	"greenout/comp/token"
)

// MaxProfundidade é o limite de chamadas de função aninhadas.
const MaxProfundidade = 5000

// Env é um ambiente de variáveis encadeado ao ambiente que o criou.
type Env struct {
	vars map[string]Valor
	pai  *Env
}

// NovoEnv cria um ambiente filho de pai (que pode ser nil).
func NovoEnv(pai *Env) *Env { return &Env{vars: map[string]Valor{}, pai: pai} }

// Definir cria ou sobrescreve a variável neste ambiente.
func (e *Env) Definir(nome string, v Valor) { e.vars[nome] = v }

// Buscar procura a variável deste ambiente para fora.
func (e *Env) Buscar(nome string) (Valor, bool) {
	for a := e; a != nil; a = a.pai {
		if v, ok := a.vars[nome]; ok {
			return v, true
		}
	}
	return nil, false
}

// Atribuir altera a variável existente mais próxima; false se não existe.
func (e *Env) Atribuir(nome string, v Valor) bool {
	for a := e; a != nil; a = a.pai {
		if _, ok := a.vars[nome]; ok {
			a.vars[nome] = v
			return true
		}
	}
	return false
}

// Interp mantém o estado entre execuções (útil para um REPL).
type Interp struct {
	universo *Env // embutidos
	global   *Env
	prof     int
}

// Novo cria um interpretador vazio.
func Novo() *Interp {
	u := NovoEnv(nil)
	return &Interp{universo: u, global: NovoEnv(u)}
}

// DefinirEmbutido registra um valor visível em todos os programas.
func (in *Interp) DefinirEmbutido(nome string, v Valor) { in.universo.Definir(nome, v) }

// Global devolve o ambiente global, que persiste entre chamadas a Executar.
func (in *Interp) Global() *Env { return in.global }

// ComPosicao devolve err como *token.Erro com a posição dada, mantendo a
// posição original se o erro já a tiver.
func ComPosicao(err error, pos token.Posicao) error {
	var te *token.Erro
	if errors.As(err, &te) {
		return err
	}
	return &token.Erro{Posicao: pos, Msg: err.Error()}
}

func erroEm(pos token.Posicao, formato string, args ...any) error {
	return token.Errorf(pos, formato, args...)
}

// Executar roda o programa no ambiente global e devolve o valor do último
// comando de expressão de nível superior (Nulo se não houver).
func (in *Interp) Executar(prog *ast.Programa) (Valor, error) {
	in.prof = 0
	in.icar(prog.Comandos, in.global)
	var ultimo Valor = Nulo{}
	for _, c := range prog.Comandos {
		if ce, ok := c.(*ast.ComandoExpr); ok {
			v, err := in.avaliar(ce.Expr, in.global)
			if err != nil {
				return nil, err
			}
			ultimo = v
			continue
		}
		_, retornou, err := in.executar(c, in.global)
		if err != nil {
			return nil, err
		}
		if retornou {
			return nil, erroEm(c.Pos(), "'return' fora de função")
		}
	}
	return ultimo, nil
}

// icar define as funções declaradas com "fn nome" no início do bloco, para
// que possam ser chamadas antes da declaração e entre si.
func (in *Interp) icar(cs []ast.Comando, env *Env) {
	for _, c := range cs {
		if f, ok := c.(*ast.DeclFuncao); ok {
			env.Definir(f.Nome.Nome, &Funcao{Nome: f.Nome.Nome, Params: ast.NomesParams(f.Params), Corpo: f.Corpo, Env: env})
		}
	}
}

// executarLista roda comandos em sequência no ambiente dado. O segundo
// resultado indica que um return foi executado.
func (in *Interp) executarLista(cs []ast.Comando, env *Env) (Valor, bool, error) {
	for _, c := range cs {
		v, retornou, err := in.executar(c, env)
		if err != nil || retornou {
			return v, retornou, err
		}
	}
	return nil, false, nil
}

func (in *Interp) executar(c ast.Comando, env *Env) (Valor, bool, error) {
	switch n := c.(type) {
	case *ast.Let:
		v, err := in.avaliar(n.Valor, env)
		if err != nil {
			return nil, false, err
		}
		if _, lit := n.Valor.(*ast.LiteralFuncao); lit {
			v.(*Funcao).Nome = n.Nome.Nome // só literais recebem o nome da variável
		}
		env.Definir(n.Nome.Nome, v)
	case *ast.Atribuicao:
		return nil, false, in.atribuir(n, env)
	case *ast.Retorno:
		if n.Valor == nil {
			return Nulo{}, true, nil
		}
		v, err := in.avaliar(n.Valor, env)
		return v, err == nil, err
	case *ast.ComandoExpr:
		_, err := in.avaliar(n.Expr, env)
		return nil, false, err
	case *ast.Bloco:
		return in.bloco(n, env)
	case *ast.Se:
		ok, err := in.condicao(n.Cond, env)
		if err != nil {
			return nil, false, err
		}
		if ok {
			return in.bloco(n.Entao, env)
		}
		if n.Senao != nil {
			return in.executar(n.Senao, env)
		}
	case *ast.Enquanto:
		for {
			ok, err := in.condicao(n.Cond, env)
			if err != nil || !ok {
				return nil, false, err
			}
			if v, retornou, err := in.bloco(n.Corpo, env); err != nil || retornou {
				return v, retornou, err
			}
		}
	case *ast.DeclFuncao:
		// já definida por icar
	}
	return nil, false, nil
}

func (in *Interp) bloco(b *ast.Bloco, env *Env) (Valor, bool, error) {
	filho := NovoEnv(env)
	in.icar(b.Comandos, filho)
	return in.executarLista(b.Comandos, filho)
}

func (in *Interp) condicao(e ast.Expressao, env *Env) (bool, error) {
	v, err := in.avaliar(e, env)
	if err != nil {
		return false, err
	}
	b, err := ComoBool(v)
	if err != nil {
		return false, ComPosicao(err, e.Pos())
	}
	return b, nil
}

func (in *Interp) atribuir(n *ast.Atribuicao, env *Env) error {
	switch alvo := n.Alvo.(type) {
	case *ast.Identificador:
		v, err := in.avaliar(n.Valor, env)
		if err != nil {
			return err
		}
		if !env.Atribuir(alvo.Nome, v) {
			return erroEm(alvo.Posicao, "variável '%s' não declarada", alvo.Nome)
		}
	case *ast.Acesso:
		arr, err := in.avaliar(alvo.Alvo, env)
		if err != nil {
			return err
		}
		idx, err := in.avaliar(alvo.Indice, env)
		if err != nil {
			return err
		}
		v, err := in.avaliar(n.Valor, env)
		if err != nil {
			return err
		}
		if err := AtribuirIndice(arr, idx, v); err != nil {
			return ComPosicao(err, alvo.Posicao)
		}
	default:
		return erroEm(n.Posicao, "alvo de atribuição inválido")
	}
	return nil
}

func (in *Interp) avaliar(e ast.Expressao, env *Env) (Valor, error) {
	switch n := e.(type) {
	case *ast.Inteiro:
		return Inteiro(n.Valor), nil
	case *ast.Booleano:
		return Booleano(n.Valor), nil
	case *ast.Texto:
		return Texto(n.Valor), nil
	case *ast.Identificador:
		if v, ok := env.Buscar(n.Nome); ok {
			return v, nil
		}
		return nil, erroEm(n.Posicao, "variável '%s' não declarada", n.Nome)
	case *ast.ArrayLit:
		elems := make([]Valor, len(n.Elementos))
		for i, el := range n.Elementos {
			v, err := in.avaliar(el, env)
			if err != nil {
				return nil, err
			}
			elems[i] = v
		}
		return &Array{Elems: elems}, nil
	case *ast.Prefixo:
		v, err := in.avaliar(n.Dir, env)
		if err != nil {
			return nil, err
		}
		r, err := Prefixar(n.Op, v)
		if err != nil {
			return nil, ComPosicao(err, n.Posicao)
		}
		return r, nil
	case *ast.Infixo:
		return in.infixo(n, env)
	case *ast.Acesso:
		alvo, err := in.avaliar(n.Alvo, env)
		if err != nil {
			return nil, err
		}
		idx, err := in.avaliar(n.Indice, env)
		if err != nil {
			return nil, err
		}
		r, err := Indexar(alvo, idx)
		if err != nil {
			return nil, ComPosicao(err, n.Posicao)
		}
		return r, nil
	case *ast.Chamada:
		f, err := in.avaliar(n.Funcao, env)
		if err != nil {
			return nil, err
		}
		args := make([]Valor, len(n.Args))
		for i, a := range n.Args {
			if args[i], err = in.avaliar(a, env); err != nil {
				return nil, err
			}
		}
		return in.Chamar(f, args, n.Posicao)
	case *ast.LiteralFuncao:
		return &Funcao{Params: ast.NomesParams(n.Params), Corpo: n.Corpo, Env: env}, nil
	}
	return nil, erroEm(e.Pos(), "expressão desconhecida %T", e)
}

func (in *Interp) infixo(n *ast.Infixo, env *Env) (Valor, error) {
	esq, err := in.avaliar(n.Esq, env)
	if err != nil {
		return nil, err
	}
	if n.Op == "&&" || n.Op == "||" {
		l, err := ComoBool(esq)
		if err != nil {
			return nil, ComPosicao(err, n.Posicao)
		}
		if (n.Op == "&&" && !l) || (n.Op == "||" && l) {
			return Booleano(l), nil
		}
		dir, err := in.avaliar(n.Dir, env)
		if err != nil {
			return nil, err
		}
		r, err := ComoBool(dir)
		if err != nil {
			return nil, ComPosicao(err, n.Posicao)
		}
		return Booleano(r), nil
	}
	dir, err := in.avaliar(n.Dir, env)
	if err != nil {
		return nil, err
	}
	r, err := Operar(n.Op, esq, dir)
	if err != nil {
		return nil, ComPosicao(err, n.Posicao)
	}
	return r, nil
}

// Chamar aplica uma função (de Mini ou embutida) a argumentos; pos é o ponto
// da chamada, usado nos erros.
func (in *Interp) Chamar(f Valor, args []Valor, pos token.Posicao) (Valor, error) {
	switch fn := f.(type) {
	case *Nativa:
		if fn.Aridade >= 0 && fn.Aridade != len(args) {
			return nil, erroEm(pos, "'%s' espera %d argumento(s), recebeu %d", fn.Nome, fn.Aridade, len(args))
		}
		v, err := fn.Fn(args)
		if err != nil {
			return nil, ComPosicao(err, pos)
		}
		if v == nil {
			v = Nulo{}
		}
		return v, nil
	case *Funcao:
		if len(fn.Params) != len(args) {
			return nil, erroEm(pos, "%s espera %d argumento(s), recebeu %d", NomeParaErro(fn.Nome), len(fn.Params), len(args))
		}
		if in.prof >= MaxProfundidade {
			return nil, erroEm(pos, "estouro de pilha: recursão profunda demais")
		}
		in.prof++
		defer func() { in.prof-- }()
		env := NovoEnv(fn.Env)
		for i, p := range fn.Params {
			env.Definir(p, args[i])
		}
		in.icar(fn.Corpo.Comandos, env)
		v, retornou, err := in.executarLista(fn.Corpo.Comandos, env)
		if err != nil {
			return nil, err
		}
		if !retornou {
			return Nulo{}, nil
		}
		return v, nil
	}
	return nil, erroEm(pos, "valor do tipo %s não é chamável", f.Tipo())
}

// NomeParaErro formata o nome de uma função para mensagens de erro:
// 'nome' entre aspas, ou "função" quando é anônima.
func NomeParaErro(nome string) string {
	if nome == "" {
		return "função"
	}
	return fmt.Sprintf("'%s'", nome)
}
