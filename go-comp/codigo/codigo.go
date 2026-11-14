// Pacote codigo define o conjunto de instruções (bytecode) da máquina de
// pilha de Mini, as estruturas de programa compilado e um disassembler.
//
// O modelo de variáveis espelha o interpretador: cada chamada de função e
// cada bloco com declarações cria um ambiente (OpEscopo); uma variável é
// endereçada por (A = quantos ambientes subir, B = posição no ambiente).
package codigo

import (
	"fmt"
	"strings"

	"greenout/comp/interp"
	"greenout/comp/token"
)

// Opcode identifica uma instrução.
type Opcode byte

const (
	OpConst              Opcode = iota // A: índice em Constantes; empilha
	OpNulo                             // empilha nulo
	OpVerdadeiro                       // empilha true
	OpFalso                            // empilha false
	OpPop                              // descarta o topo
	OpCarregar                         // A: saltos, B: posição; empilha a variável
	OpGuardar                          // A: saltos, B: posição; desempilha e grava
	OpEmbutido                         // A: índice da constante com o nome; empilha a função embutida
	OpSoma                             // b a -> a+b (demais binários idem)
	OpSub                              //
	OpMul                              //
	OpDiv                              //
	OpResto                            //
	OpIgual                            //
	OpDiferente                        //
	OpMenor                            //
	OpMenorIgual                       //
	OpMaior                            //
	OpMaiorIgual                       //
	OpNeg                              // -topo
	OpNao                              // !topo
	OpSalto                            // A: destino
	OpSaltoSeFalso                     // A: destino; desempilha, exige bool
	OpManterSeFalso                    // A: destino; exige bool; se false salta mantendo, senão desempilha
	OpManterSeVerdadeiro               // A: destino; exige bool; se true salta mantendo, senão desempilha
	OpExigirBool                       // erro se o topo não for bool
	OpArray                            // A: n; desempilha n elementos e empilha o array
	OpIndice                           // idx alvo -> alvo[idx]
	OpGuardarIndice                    // valor idx alvo -> (grava alvo[idx] = valor)
	OpFecho                            // A: índice em Funcoes; empilha closure sobre o ambiente atual
	OpChamar                           // A: nº de argumentos; função fica abaixo dos argumentos
	OpRetornar                         // desempilha o resultado e volta ao chamador
	OpEscopo                           // A: nº de posições; abre ambiente de bloco
	OpFimEscopo                        // fecha o ambiente de bloco
	numOpcodes
)

type infoOp struct {
	nome      string
	operandos int
	operador  string // para operadores aritméticos/lógicos
}

var infos = [numOpcodes]infoOp{
	OpConst: {"CONST", 1, ""}, OpNulo: {"NULO", 0, ""}, OpVerdadeiro: {"VERDADEIRO", 0, ""},
	OpFalso: {"FALSO", 0, ""}, OpPop: {"POP", 0, ""}, OpCarregar: {"CARREGAR", 2, ""},
	OpGuardar: {"GUARDAR", 2, ""}, OpEmbutido: {"EMBUTIDO", 1, ""},
	OpSoma: {"SOMA", 0, "+"}, OpSub: {"SUB", 0, "-"}, OpMul: {"MUL", 0, "*"}, OpDiv: {"DIV", 0, "/"},
	OpResto: {"RESTO", 0, "%"}, OpIgual: {"IGUAL", 0, "=="}, OpDiferente: {"DIFERENTE", 0, "!="},
	OpMenor: {"MENOR", 0, "<"}, OpMenorIgual: {"MENOR_IGUAL", 0, "<="}, OpMaior: {"MAIOR", 0, ">"},
	OpMaiorIgual: {"MAIOR_IGUAL", 0, ">="}, OpNeg: {"NEG", 0, "-"}, OpNao: {"NAO", 0, "!"},
	OpSalto: {"SALTO", 1, ""}, OpSaltoSeFalso: {"SALTO_SE_FALSO", 1, ""},
	OpManterSeFalso: {"MANTER_SE_FALSO", 1, ""}, OpManterSeVerdadeiro: {"MANTER_SE_VERDADEIRO", 1, ""},
	OpExigirBool: {"EXIGIR_BOOL", 0, ""}, OpArray: {"ARRAY", 1, ""}, OpIndice: {"INDICE", 0, ""},
	OpGuardarIndice: {"GUARDAR_INDICE", 0, ""}, OpFecho: {"FECHO", 1, ""}, OpChamar: {"CHAMAR", 1, ""},
	OpRetornar: {"RETORNAR", 0, ""}, OpEscopo: {"ESCOPO", 1, ""}, OpFimEscopo: {"FIM_ESCOPO", 0, ""},
}

// Valido informa se op é uma instrução conhecida.
func (op Opcode) Valido() bool { return op < numOpcodes }

func (op Opcode) String() string {
	if !op.Valido() {
		return fmt.Sprintf("OP(%d)", byte(op))
	}
	return infos[op].nome
}

// Operandos devolve quantos operandos (A, B) a instrução usa.
func (op Opcode) Operandos() int {
	if !op.Valido() {
		return 0
	}
	return infos[op].operandos
}

// Operador devolve o símbolo do operador (ex.: "+") para instruções
// aritméticas, de comparação e unárias; vazio para as demais.
func (op Opcode) Operador() string {
	if !op.Valido() {
		return ""
	}
	return infos[op].operador
}

// DeOperador devolve o opcode binário de um operador (ex.: "<=").
func DeOperador(operador string) (Opcode, bool) {
	for op := OpSoma; op <= OpMaiorIgual; op++ {
		if infos[op].operador == operador {
			return op, true
		}
	}
	return 0, false
}

// Instrucao é um opcode com até dois operandos inteiros.
type Instrucao struct {
	Op   Opcode
	A, B int
}

// Funcao é o código compilado de uma função (ou do programa principal).
type Funcao struct {
	Nome     string
	Aridade  int
	NumVars  int // posições do ambiente da chamada: parâmetros e declarações
	Codigo   []Instrucao
	Posicoes []token.Posicao // posição de origem de cada instrução
}

// Emitir acrescenta uma instrução e devolve seu índice.
func (f *Funcao) Emitir(op Opcode, a, b int, pos token.Posicao) int {
	f.Codigo = append(f.Codigo, Instrucao{op, a, b})
	f.Posicoes = append(f.Posicoes, pos)
	return len(f.Codigo) - 1
}

// Remendar ajusta o operando A de um salto já emitido para o destino dado.
func (f *Funcao) Remendar(indice, destino int) { f.Codigo[indice].A = destino }

// Programa é o resultado da compilação.
type Programa struct {
	Principal  *Funcao
	Funcoes    []*Funcao
	Constantes []interp.Valor
}

// Validar confere a consistência estrutural do programa: opcodes conhecidos,
// destinos de salto e índices de tabelas dentro dos limites e tamanho das
// tabelas de posições. Útil para detectar erros do compilador.
func (p *Programa) Validar() error {
	todas := append([]*Funcao{p.Principal}, p.Funcoes...)
	for _, f := range todas {
		if len(f.Posicoes) != len(f.Codigo) {
			return fmt.Errorf("%s: %d posições para %d instruções", f.Nome, len(f.Posicoes), len(f.Codigo))
		}
		for i, ins := range f.Codigo {
			if !ins.Op.Valido() {
				return fmt.Errorf("%s[%d]: opcode inválido %d", f.Nome, i, byte(ins.Op))
			}
			var err error
			switch ins.Op {
			case OpSalto, OpSaltoSeFalso, OpManterSeFalso, OpManterSeVerdadeiro:
				if ins.A < 0 || ins.A > len(f.Codigo) {
					err = fmt.Errorf("destino de salto %d fora de [0,%d]", ins.A, len(f.Codigo))
				}
			case OpConst, OpEmbutido:
				if ins.A < 0 || ins.A >= len(p.Constantes) {
					err = fmt.Errorf("constante %d inexistente", ins.A)
				}
			case OpFecho:
				if ins.A < 0 || ins.A >= len(p.Funcoes) {
					err = fmt.Errorf("função %d inexistente", ins.A)
				}
			case OpCarregar, OpGuardar:
				if ins.A < 0 || ins.B < 0 {
					err = fmt.Errorf("endereço de variável negativo (%d, %d)", ins.A, ins.B)
				}
			case OpArray, OpChamar, OpEscopo:
				if ins.A < 0 {
					err = fmt.Errorf("operando negativo %d", ins.A)
				}
			}
			if err != nil {
				return fmt.Errorf("%s[%d] %s: %w", f.Nome, i, ins.Op, err)
			}
		}
	}
	return nil
}

// Desmontar produz uma listagem legível (disassembler) do programa inteiro.
func Desmontar(p *Programa) string {
	var sb strings.Builder
	desmontarFuncao(&sb, p, p.Principal)
	for _, f := range p.Funcoes {
		sb.WriteString("\n")
		desmontarFuncao(&sb, p, f)
	}
	return sb.String()
}

// DesmontarFuncao lista apenas uma função.
func DesmontarFuncao(p *Programa, f *Funcao) string {
	var sb strings.Builder
	desmontarFuncao(&sb, p, f)
	return sb.String()
}

func nomeFuncao(f *Funcao) string {
	if f.Nome == "" {
		return "<anônima>"
	}
	return f.Nome
}

func desmontarFuncao(sb *strings.Builder, p *Programa, f *Funcao) {
	fmt.Fprintf(sb, "== %s (aridade %d, vars %d) ==\n", nomeFuncao(f), f.Aridade, f.NumVars)
	for i, ins := range f.Codigo {
		pos := ""
		if i < len(f.Posicoes) && f.Posicoes[i].Valida() {
			pos = f.Posicoes[i].String()
		}
		fmt.Fprintf(sb, "%04d %6s  %-21s%s\n", i, pos, ins.Op, operandos(p, ins))
	}
}

// operandos formata os operandos de uma instrução com um comentário útil.
func operandos(p *Programa, ins Instrucao) string {
	switch ins.Op {
	case OpConst:
		if ins.A >= 0 && ins.A < len(p.Constantes) {
			return fmt.Sprintf("%d  ; %s", ins.A, interp.Repr(p.Constantes[ins.A]))
		}
	case OpEmbutido:
		if ins.A >= 0 && ins.A < len(p.Constantes) {
			return fmt.Sprintf("%d  ; %s", ins.A, p.Constantes[ins.A])
		}
	case OpFecho:
		if ins.A >= 0 && ins.A < len(p.Funcoes) {
			return fmt.Sprintf("%d  ; %s", ins.A, nomeFuncao(p.Funcoes[ins.A]))
		}
	case OpSalto, OpSaltoSeFalso, OpManterSeFalso, OpManterSeVerdadeiro:
		return fmt.Sprintf("-> %04d", ins.A)
	case OpCarregar, OpGuardar:
		return fmt.Sprintf("saltos=%d pos=%d", ins.A, ins.B)
	}
	switch ins.Op.Operandos() {
	case 1:
		return fmt.Sprint(ins.A)
	case 2:
		return fmt.Sprintf("%d %d", ins.A, ins.B)
	}
	return ""
}
