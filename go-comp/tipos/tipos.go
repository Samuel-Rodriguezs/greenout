// Pacote tipos implementa uma verificação de tipos gradual para Mini.
//
// Não há anotações: tipos de literais e operadores são inferidos, e
// parâmetros de função começam como Qualquer (desconhecido). Qualquer é
// compatível com todos os tipos, de modo que só são reportados conflitos
// entre tipos conhecidos, como somar inteiro com texto.
package tipos

import (
	"fmt"
	"strings"

	"greenout/comp/ast"
	"greenout/comp/simbolos"
	"greenout/comp/token"
)

// Base é o tipo de uma expressão.
type Base string

const (
	Int      Base = "int"
	Bool     Base = "bool"
	Texto    Base = "texto"
	Array    Base = "array"
	Func     Base = "função"
	Nulo     Base = "nulo"
	Qualquer Base = "qualquer"
)

// Assinatura descreve uma função. Aridade -1 significa variádica; Params
// pode ser mais curto que a aridade (parâmetros restantes são Qualquer).
type Assinatura struct {
	Aridade int
	Params  []Base
	Ret     Base
}

// Opcoes configura a verificação.
type Opcoes struct {
	Embutidos map[string]*Assinatura
}

// PadraoEmbutidos devolve as assinaturas de len, print e push.
func PadraoEmbutidos() map[string]*Assinatura {
	return map[string]*Assinatura{
		"len":   {Aridade: 1, Params: []Base{Qualquer}, Ret: Int},
		"print": {Aridade: -1, Ret: Nulo},
		"push":  {Aridade: 2, Params: []Base{Array, Qualquer}, Ret: Array},
	}
}

// Resultado contém os erros e o tipo inferido de cada expressão visitada.
type Resultado struct {
	Erros []*token.Erro
	Tipos map[ast.Expressao]Base
}

// Compativel informa se dois tipos podem coexistir (iguais ou algum Qualquer).
func Compativel(a, b Base) bool { return a == b || a == Qualquer || b == Qualquer }

type info struct {
	tipo Base
	sig  *Assinatura
}

type verificador struct {
	tab      *simbolos.Tabela
	res      *Resultado
	sigs     map[*ast.LiteralFuncao]*Assinatura
	retornos []*[]Base // pilha de coletores de tipos de return
}

// Verificar checa os tipos do programa.
func Verificar(prog *ast.Programa, op Opcoes) *Resultado {
	v := &verificador{
		tab:  simbolos.Nova(),
		res:  &Resultado{Tipos: map[ast.Expressao]Base{}},
		sigs: map[*ast.LiteralFuncao]*Assinatura{},
	}
	for nome, sig := range op.Embutidos {
		v.tab.DeclararEmbutido(nome, &info{tipo: Func, sig: sig})
	}
	v.comandos(prog.Comandos)
	return v.res
}

func (v *verificador) erro(pos token.Posicao, formato string, args ...any) {
	v.res.Erros = append(v.res.Erros, token.Errorf(pos, formato, args...))
}

func (v *verificador) declarar(id *ast.Identificador, cat simbolos.Categoria, inf *info) {
	if s, err := v.tab.Declarar(id.Nome, cat, id.Posicao); err == nil {
		s.Dado = inf
	}
}

func infoDe(s *simbolos.Simbolo) *info {
	if i, ok := s.Dado.(*info); ok {
		return i
	}
	return &info{tipo: Qualquer}
}

func (v *verificador) comandos(cs []ast.Comando) {
	for _, c := range cs {
		if f, ok := c.(*ast.DeclFuncao); ok {
			v.declarar(f.Nome, simbolos.Funcao, &info{tipo: Func, sig: novaSig(len(f.Params))})
		}
	}
	for _, c := range cs {
		v.comando(c)
	}
}

func novaSig(aridade int) *Assinatura { return &Assinatura{Aridade: aridade, Ret: Qualquer} }

func (v *verificador) bloco(b *ast.Bloco) {
	v.tab.Entrar(false)
	v.comandos(b.Comandos)
	v.tab.Sair()
}

// termina informa se a sequência sempre encerra com return.
func termina(cs []ast.Comando) bool {
	if len(cs) == 0 {
		return false
	}
	switch n := cs[len(cs)-1].(type) {
	case *ast.Retorno:
		return true
	case *ast.Bloco:
		return termina(n.Comandos)
	case *ast.Se:
		if n.Senao == nil || !termina(n.Entao.Comandos) {
			return false
		}
		return termina([]ast.Comando{n.Senao})
	}
	return false
}

// funcao verifica o corpo e preenche o tipo de retorno em sig.
func (v *verificador) funcao(params []*ast.Identificador, corpo *ast.Bloco, sig *Assinatura) {
	v.tab.Entrar(true)
	for _, p := range params {
		v.declarar(p, simbolos.Parametro, &info{tipo: Qualquer})
	}
	var rets []Base
	v.retornos = append(v.retornos, &rets)
	v.comandos(corpo.Comandos)
	v.retornos = v.retornos[:len(v.retornos)-1]
	v.tab.Sair()

	sig.Ret = Nulo
	if len(rets) > 0 {
		sig.Ret = rets[0]
		for _, r := range rets[1:] {
			if r != sig.Ret {
				sig.Ret = Qualquer
			}
		}
		if !termina(corpo.Comandos) && sig.Ret != Nulo {
			sig.Ret = Qualquer // pode "cair" no fim e devolver nulo
		}
	}
}

func (v *verificador) comando(c ast.Comando) {
	switch n := c.(type) {
	case *ast.Let:
		if lit, ok := n.Valor.(*ast.LiteralFuncao); ok {
			sig := novaSig(len(lit.Params))
			v.sigs[lit] = sig
			v.declarar(n.Nome, simbolos.Variavel, &info{tipo: Func, sig: sig})
			v.expr(lit)
			return
		}
		t := v.expr(n.Valor)
		v.declarar(n.Nome, simbolos.Variavel, &info{tipo: t, sig: v.sigDe(n.Valor)})
	case *ast.DeclFuncao:
		s, _ := v.tab.Resolver(n.Nome.Nome)
		sig := novaSig(len(n.Params))
		if s != nil && infoDe(s).sig != nil {
			sig = infoDe(s).sig
		}
		v.funcao(n.Params, n.Corpo, sig)
	case *ast.Atribuicao:
		v.atribuicao(n)
	case *ast.Retorno:
		t := Nulo
		if n.Valor != nil {
			t = v.expr(n.Valor)
		}
		if len(v.retornos) > 0 {
			col := v.retornos[len(v.retornos)-1]
			*col = append(*col, t)
		}
	case *ast.ComandoExpr:
		v.expr(n.Expr)
	case *ast.Bloco:
		v.bloco(n)
	case *ast.Se:
		v.condicao(n.Cond)
		v.bloco(n.Entao)
		if n.Senao != nil {
			v.comando(n.Senao)
		}
	case *ast.Enquanto:
		v.condicao(n.Cond)
		v.bloco(n.Corpo)
	}
}

func (v *verificador) condicao(e ast.Expressao) {
	if t := v.expr(e); !Compativel(t, Bool) {
		v.erro(e.Pos(), "condição deve ser bool, recebeu %s", t)
	}
}

func (v *verificador) atribuicao(n *ast.Atribuicao) {
	valor := v.expr(n.Valor)
	switch alvo := n.Alvo.(type) {
	case *ast.Identificador:
		s, ok := v.tab.Resolver(alvo.Nome)
		if !ok {
			return
		}
		inf := infoDe(s)
		if !Compativel(inf.tipo, valor) {
			v.erro(n.Posicao, "não é possível atribuir %s à variável '%s' do tipo %s", valor, alvo.Nome, inf.tipo)
			return
		}
		inf.sig = nil // o valor da variável mudou: assinatura deixa de ser confiável
	case *ast.Acesso:
		alvoT := v.expr(alvo.Alvo)
		if alvoT == Texto {
			v.erro(alvo.Posicao, "texto não permite atribuição por índice")
		} else if !Compativel(alvoT, Array) {
			v.erro(alvo.Posicao, "indexação requer array, recebeu %s", alvoT)
		}
		if it := v.expr(alvo.Indice); !Compativel(it, Int) {
			v.erro(alvo.Indice.Pos(), "índice deve ser int, recebeu %s", it)
		}
	}
}

// sigDe devolve a assinatura conhecida de uma expressão de função, ou nil.
func (v *verificador) sigDe(e ast.Expressao) *Assinatura {
	switch n := e.(type) {
	case *ast.Identificador:
		if s, ok := v.tab.Resolver(n.Nome); ok {
			return infoDe(s).sig
		}
	case *ast.LiteralFuncao:
		return v.sigs[n]
	}
	return nil
}

func (v *verificador) expr(e ast.Expressao) Base {
	t := v.tipoExpr(e)
	v.res.Tipos[e] = t
	return t
}

func (v *verificador) tipoExpr(e ast.Expressao) Base {
	switch n := e.(type) {
	case *ast.Inteiro:
		return Int
	case *ast.Booleano:
		return Bool
	case *ast.Texto:
		return Texto
	case *ast.Identificador:
		if s, ok := v.tab.Resolver(n.Nome); ok {
			return infoDe(s).tipo
		}
		return Qualquer // nome indefinido: tarefa da análise semântica
	case *ast.ArrayLit:
		for _, el := range n.Elementos {
			v.expr(el)
		}
		return Array
	case *ast.Prefixo:
		return v.prefixo(n)
	case *ast.Infixo:
		return v.infixo(n)
	case *ast.Acesso:
		alvo := v.expr(n.Alvo)
		if it := v.expr(n.Indice); !Compativel(it, Int) {
			v.erro(n.Indice.Pos(), "índice deve ser int, recebeu %s", it)
		}
		switch alvo {
		case Texto:
			return Texto
		case Array, Qualquer:
			return Qualquer
		}
		v.erro(n.Posicao, "indexação requer array ou texto, recebeu %s", alvo)
		return Qualquer
	case *ast.Chamada:
		return v.chamada(n)
	case *ast.LiteralFuncao:
		sig, ok := v.sigs[n]
		if !ok {
			sig = novaSig(len(n.Params))
			v.sigs[n] = sig
		}
		v.funcao(n.Params, n.Corpo, sig)
		return Func
	}
	return Qualquer
}

func (v *verificador) prefixo(n *ast.Prefixo) Base {
	t := v.expr(n.Dir)
	alvo := Int
	if n.Op == "!" {
		alvo = Bool
	}
	if !Compativel(t, alvo) {
		v.erro(n.Posicao, "operador '%s' requer %s, recebeu %s", n.Op, alvo, t)
	}
	return alvo
}

func (v *verificador) infixo(n *ast.Infixo) Base {
	l, r := v.expr(n.Esq), v.expr(n.Dir)
	conflito := func(esperado string) {
		v.erro(n.Posicao, "operador '%s' requer %s, recebeu %s e %s", n.Op, esperado, l, r)
	}
	switch n.Op {
	case "-", "*", "/", "%":
		if !Compativel(l, Int) || !Compativel(r, Int) {
			conflito("int")
		}
		return Int
	case "+":
		switch {
		case l == Int && r == Int, l == Int && r == Qualquer, l == Qualquer && r == Int:
			return Int
		case l == Texto && r == Texto, l == Texto && r == Qualquer, l == Qualquer && r == Texto:
			return Texto
		case l == Qualquer && r == Qualquer:
			return Qualquer
		}
		conflito("dois int ou dois texto")
		return Qualquer
	case "<", "<=", ">", ">=":
		if !Compativel(l, r) || (l != Qualquer && l != Int && l != Texto) || (r != Qualquer && r != Int && r != Texto) {
			conflito("dois int ou dois texto")
		}
		return Bool
	case "==", "!=":
		if !Compativel(l, r) {
			v.erro(n.Posicao, "comparação entre tipos incompatíveis: %s e %s", l, r)
		}
		return Bool
	case "&&", "||":
		if !Compativel(l, Bool) || !Compativel(r, Bool) {
			conflito("bool")
		}
		return Bool
	}
	return Qualquer
}

func (v *verificador) chamada(n *ast.Chamada) Base {
	callee := v.expr(n.Funcao)
	args := make([]Base, len(n.Args))
	for i, a := range n.Args {
		args[i] = v.expr(a)
	}
	if !Compativel(callee, Func) {
		v.erro(n.Posicao, "valor do tipo %s não é chamável", callee)
		return Qualquer
	}
	sig := v.sigDe(n.Funcao)
	if sig == nil {
		return Qualquer
	}
	nome := "função"
	if id, ok := n.Funcao.(*ast.Identificador); ok {
		nome = "'" + id.Nome + "'"
	}
	if sig.Aridade >= 0 && sig.Aridade != len(args) {
		v.erro(n.Posicao, "%s espera %d argumento(s), recebeu %d", nome, sig.Aridade, len(args))
		return sig.Ret
	}
	for i, a := range args {
		if i < len(sig.Params) && !Compativel(sig.Params[i], a) {
			v.erro(n.Args[i].Pos(), "argumento %d de %s deveria ser %s, recebeu %s", i+1, nome, sig.Params[i], a)
		}
	}
	return sig.Ret
}

// Mensagens devolve os erros no formato "linha:coluna: mensagem".
func (r *Resultado) Mensagens() []string {
	ms := make([]string, len(r.Erros))
	for i, e := range r.Erros {
		ms[i] = e.Error()
	}
	return ms
}

func (a *Assinatura) String() string {
	ps := make([]string, len(a.Params))
	for i, p := range a.Params {
		ps[i] = string(p)
	}
	return fmt.Sprintf("fn(%s) -> %s", strings.Join(ps, ", "), a.Ret)
}
