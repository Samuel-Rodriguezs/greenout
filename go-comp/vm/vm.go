// Pacote vm implementa a máquina virtual de pilha que executa o bytecode de
// Mini, com uma pilha de frames de chamada e ambientes encadeados que
// reproduzem as closures do interpretador.
package vm

import (
	"fmt"

	"greenout/comp/codigo"
	"greenout/comp/interp"
)

// ambiente é o espaço de variáveis de uma chamada de função ou de um bloco.
type ambiente struct {
	vars []interp.Valor
	pai  *ambiente
}

// Fecho é uma função do bytecode junto ao ambiente em que foi criada.
type Fecho struct {
	Fn  *codigo.Funcao
	env *ambiente
}

func (*Fecho) Tipo() string { return "função" }
func (f *Fecho) String() string {
	if f.Fn.Nome == "" {
		return "<função>"
	}
	return "<função " + f.Fn.Nome + ">"
}

// frame é uma chamada ativa.
type frame struct {
	fn   *codigo.Funcao
	ip   int
	env  *ambiente
	base int // altura da pilha ao entrar; o resultado é empilhado aqui
}

// VM executa um programa compilado.
type VM struct {
	prog      *codigo.Programa
	embutidos map[string]*interp.Nativa
	pilha     []interp.Valor
	frames    []frame
}

// Novo prepara uma VM. As funções nativas recebem os argumentos em uma fatia
// que aponta para a pilha e não devem retê-la depois de retornar.
func Novo(prog *codigo.Programa, embutidos map[string]*interp.Nativa) *VM {
	return &VM{prog: prog, embutidos: embutidos}
}

func (m *VM) empilhar(v interp.Valor) { m.pilha = append(m.pilha, v) }

func (m *VM) desempilhar() interp.Valor {
	n := len(m.pilha) - 1
	v := m.pilha[n]
	m.pilha[n] = nil
	m.pilha = m.pilha[:n]
	return v
}

// Executar roda o programa principal até o fim ou até o primeiro erro.
func (m *VM) Executar() error {
	m.pilha = make([]interp.Valor, 0, 256)
	m.frames = m.frames[:0]
	principal := m.prog.Principal
	m.frames = append(m.frames, frame{fn: principal, env: &ambiente{vars: make([]interp.Valor, principal.NumVars)}})
	return m.rodar()
}

func (m *VM) rodar() error {
	for {
		fr := &m.frames[len(m.frames)-1]
		if fr.ip >= len(fr.fn.Codigo) {
			return fmt.Errorf("função %q terminou sem retornar", fr.fn.Nome)
		}
		ins := fr.fn.Codigo[fr.ip]
		pos := fr.fn.Posicoes[fr.ip]
		fr.ip++

		var err error
		switch ins.Op {
		case codigo.OpConst:
			m.empilhar(m.prog.Constantes[ins.A])
		case codigo.OpNulo:
			m.empilhar(interp.Nulo{})
		case codigo.OpVerdadeiro:
			m.empilhar(interp.Booleano(true))
		case codigo.OpFalso:
			m.empilhar(interp.Booleano(false))
		case codigo.OpPop:
			m.desempilhar()
		case codigo.OpCarregar:
			e := fr.env
			for i := 0; i < ins.A; i++ {
				e = e.pai
			}
			v := e.vars[ins.B]
			if v == nil {
				err = fmt.Errorf("variável lida antes de ser inicializada")
				break
			}
			m.empilhar(v)
		case codigo.OpGuardar:
			e := fr.env
			for i := 0; i < ins.A; i++ {
				e = e.pai
			}
			e.vars[ins.B] = m.desempilhar()
		case codigo.OpEmbutido:
			nome := string(m.prog.Constantes[ins.A].(interp.Texto))
			nat, ok := m.embutidos[nome]
			if !ok {
				err = fmt.Errorf("embutido '%s' indisponível", nome)
				break
			}
			m.empilhar(nat)
		case codigo.OpSoma, codigo.OpSub, codigo.OpMul, codigo.OpDiv, codigo.OpResto,
			codigo.OpIgual, codigo.OpDiferente, codigo.OpMenor, codigo.OpMenorIgual,
			codigo.OpMaior, codigo.OpMaiorIgual:
			b, a := m.desempilhar(), m.desempilhar()
			var r interp.Valor
			if r = rapido(ins.Op, a, b); r == nil {
				r, err = interp.Operar(ins.Op.Operador(), a, b)
			}
			if err == nil {
				m.empilhar(r)
			}
		case codigo.OpNeg, codigo.OpNao:
			var r interp.Valor
			if r, err = interp.Prefixar(ins.Op.Operador(), m.desempilhar()); err == nil {
				m.empilhar(r)
			}
		case codigo.OpSalto:
			fr.ip = ins.A
		case codigo.OpSaltoSeFalso:
			var cond bool
			if cond, err = interp.ComoBool(m.desempilhar()); err == nil && !cond {
				fr.ip = ins.A
			}
		case codigo.OpManterSeFalso, codigo.OpManterSeVerdadeiro:
			var cond bool
			if cond, err = interp.ComoBool(m.pilha[len(m.pilha)-1]); err != nil {
				break
			}
			if cond == (ins.Op == codigo.OpManterSeVerdadeiro) {
				fr.ip = ins.A
			} else {
				m.desempilhar()
			}
		case codigo.OpExigirBool:
			_, err = interp.ComoBool(m.pilha[len(m.pilha)-1])
		case codigo.OpArray:
			elems := make([]interp.Valor, ins.A)
			copy(elems, m.pilha[len(m.pilha)-ins.A:])
			m.limpar(ins.A)
			m.empilhar(&interp.Array{Elems: elems})
		case codigo.OpIndice:
			idx, alvo := m.desempilhar(), m.desempilhar()
			var r interp.Valor
			if r, err = interp.Indexar(alvo, idx); err == nil {
				m.empilhar(r)
			}
		case codigo.OpGuardarIndice:
			v, idx, alvo := m.desempilhar(), m.desempilhar(), m.desempilhar()
			err = interp.AtribuirIndice(alvo, idx, v)
		case codigo.OpFecho:
			m.empilhar(&Fecho{Fn: m.prog.Funcoes[ins.A], env: fr.env})
		case codigo.OpChamar:
			err = m.chamar(ins.A)
		case codigo.OpRetornar:
			v := m.desempilhar()
			base := fr.base
			m.frames = m.frames[:len(m.frames)-1]
			if len(m.frames) == 0 {
				return nil
			}
			m.limpar(len(m.pilha) - base)
			m.empilhar(v)
		case codigo.OpEscopo:
			fr.env = &ambiente{vars: make([]interp.Valor, ins.A), pai: fr.env}
		case codigo.OpFimEscopo:
			fr.env = fr.env.pai
		default:
			err = fmt.Errorf("opcode desconhecido %s", ins.Op)
		}
		if err != nil {
			return interp.ComPosicao(err, pos)
		}
	}
}

// limpar remove n valores do topo da pilha, liberando as referências.
func (m *VM) limpar(n int) {
	topo := len(m.pilha) - n
	for i := topo; i < len(m.pilha); i++ {
		m.pilha[i] = nil
	}
	m.pilha = m.pilha[:topo]
}

// rapido trata o caso comum de dois inteiros; devolve nil se não se aplica
// (inclusive divisão por zero, que cai no caminho geral para gerar o erro).
func rapido(op codigo.Opcode, a, b interp.Valor) interp.Valor {
	x, ok := a.(interp.Inteiro)
	if !ok {
		return nil
	}
	y, ok := b.(interp.Inteiro)
	if !ok {
		return nil
	}
	switch op {
	case codigo.OpSoma:
		return x + y
	case codigo.OpSub:
		return x - y
	case codigo.OpMul:
		return x * y
	case codigo.OpMenor:
		return interp.Booleano(x < y)
	case codigo.OpMenorIgual:
		return interp.Booleano(x <= y)
	case codigo.OpMaior:
		return interp.Booleano(x > y)
	case codigo.OpMaiorIgual:
		return interp.Booleano(x >= y)
	case codigo.OpIgual:
		return interp.Booleano(x == y)
	case codigo.OpDiferente:
		return interp.Booleano(x != y)
	}
	return nil
}

// chamar executa OpChamar com n argumentos no topo e a função logo abaixo.
func (m *VM) chamar(n int) error {
	topo := len(m.pilha)
	callee := m.pilha[topo-n-1]
	args := m.pilha[topo-n:]
	switch f := callee.(type) {
	case *Fecho:
		if f.Fn.Aridade != n {
			return fmt.Errorf("%s espera %d argumento(s), recebeu %d", interp.NomeParaErro(f.Fn.Nome), f.Fn.Aridade, n)
		}
		if len(m.frames)-1 >= interp.MaxProfundidade {
			return fmt.Errorf("estouro de pilha: recursão profunda demais")
		}
		vars := make([]interp.Valor, f.Fn.NumVars)
		copy(vars, args)
		m.limpar(n + 1)
		m.frames = append(m.frames, frame{fn: f.Fn, env: &ambiente{vars: vars, pai: f.env}, base: len(m.pilha)})
		return nil
	case *interp.Nativa:
		if f.Aridade >= 0 && f.Aridade != n {
			return fmt.Errorf("'%s' espera %d argumento(s), recebeu %d", f.Nome, f.Aridade, n)
		}
		v, err := f.Fn(args)
		m.limpar(n + 1)
		if err != nil {
			return err
		}
		if v == nil {
			v = interp.Nulo{}
		}
		m.empilhar(v)
		return nil
	}
	return fmt.Errorf("valor do tipo %s não é chamável", callee.Tipo())
}
