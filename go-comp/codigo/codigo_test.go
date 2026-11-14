package codigo

import (
	"strings"
	"testing"

	"greenout/comp/interp"
	"greenout/comp/token"
)

func TestOpcodeMetadados(t *testing.T) {
	casos := []struct {
		op        Opcode
		nome      string
		operandos int
		operador  string
	}{
		{OpConst, "CONST", 1, ""},
		{OpCarregar, "CARREGAR", 2, ""},
		{OpSoma, "SOMA", 0, "+"},
		{OpMenorIgual, "MENOR_IGUAL", 0, "<="},
		{OpNeg, "NEG", 0, "-"},
		{OpRetornar, "RETORNAR", 0, ""},
		{OpFimEscopo, "FIM_ESCOPO", 0, ""},
		{Opcode(200), "OP(200)", 0, ""},
	}
	for _, c := range casos {
		if c.op.String() != c.nome || c.op.Operandos() != c.operandos || c.op.Operador() != c.operador {
			t.Errorf("%d: nome=%q operandos=%d operador=%q", byte(c.op), c.op, c.op.Operandos(), c.op.Operador())
		}
	}
	// todo opcode válido deve ter nome
	for op := Opcode(0); op < numOpcodes; op++ {
		if infos[op].nome == "" {
			t.Errorf("opcode %d sem nome", byte(op))
		}
	}
}

func TestDeOperador(t *testing.T) {
	casos := map[string]Opcode{
		"+": OpSoma, "-": OpSub, "*": OpMul, "/": OpDiv, "%": OpResto,
		"==": OpIgual, "!=": OpDiferente, "<": OpMenor, "<=": OpMenorIgual, ">": OpMaior, ">=": OpMaiorIgual,
	}
	for s, quer := range casos {
		if got, ok := DeOperador(s); !ok || got != quer {
			t.Errorf("DeOperador(%q) = %v %v, quer %v", s, got, ok, quer)
		}
	}
	for _, s := range []string{"&&", "!", "", "**"} {
		if _, ok := DeOperador(s); ok {
			t.Errorf("DeOperador(%q) não deveria existir", s)
		}
	}
}

func exemplo() *Programa {
	pos := func(l, c int) token.Posicao { return token.Posicao{Linha: l, Coluna: c} }
	dobro := &Funcao{Nome: "dobro", Aridade: 1, NumVars: 1}
	dobro.Emitir(OpCarregar, 0, 0, pos(1, 17))
	dobro.Emitir(OpConst, 1, 0, pos(1, 21))
	dobro.Emitir(OpMul, 0, 0, pos(1, 19))
	dobro.Emitir(OpRetornar, 0, 0, pos(1, 10))

	main := &Funcao{Nome: "principal", NumVars: 1}
	main.Emitir(OpFecho, 0, 0, pos(1, 1))
	main.Emitir(OpGuardar, 0, 0, pos(1, 1))
	main.Emitir(OpCarregar, 0, 0, pos(2, 7))
	main.Emitir(OpConst, 0, 0, pos(2, 13))
	main.Emitir(OpChamar, 1, 0, pos(2, 12))
	main.Emitir(OpSaltoSeFalso, 8, 0, pos(2, 1))
	main.Emitir(OpEmbutido, 2, 0, pos(3, 1))
	main.Emitir(OpPop, 0, 0, pos(3, 1))
	main.Emitir(OpNulo, 0, 0, token.Posicao{})
	main.Emitir(OpRetornar, 0, 0, token.Posicao{})
	return &Programa{
		Principal:  main,
		Funcoes:    []*Funcao{dobro},
		Constantes: []interp.Valor{interp.Inteiro(21), interp.Inteiro(2), interp.Texto("print")},
	}
}

func TestDesmontar(t *testing.T) {
	p := exemplo()
	if err := p.Validar(); err != nil {
		t.Fatalf("Validar: %v", err)
	}
	quer := []string{
		"== principal (aridade 0, vars 1) ==",
		"0000    1:1  FECHO                0  ; dobro",
		"0001    1:1  GUARDAR              saltos=0 pos=0",
		"0002    2:7  CARREGAR             saltos=0 pos=0",
		"0003   2:13  CONST                0  ; 21",
		"0004   2:12  CHAMAR               1",
		"0005    2:1  SALTO_SE_FALSO       -> 0008",
		"0006    3:1  EMBUTIDO             2  ; print",
		"0007    3:1  POP                 ",
		"0008         NULO",
		"0009         RETORNAR",
		"",
		"== dobro (aridade 1, vars 1) ==",
		"0000   1:17  CARREGAR             saltos=0 pos=0",
		"0001   1:21  CONST                1  ; 2",
		"0002   1:19  MUL                 ",
		"0003   1:10  RETORNAR            ",
	}
	got := strings.Split(strings.TrimRight(Desmontar(p), "\n"), "\n")
	if len(got) != len(quer) {
		t.Fatalf("linhas = %d, quer %d:\n%s", len(got), len(quer), Desmontar(p))
	}
	for i := range quer {
		if strings.TrimRight(got[i], " ") != strings.TrimRight(quer[i], " ") {
			t.Errorf("linha %d:\n got  %q\n quer %q", i, got[i], quer[i])
		}
	}
}

func TestDesmontarFuncaoAnonimaEConstanteTexto(t *testing.T) {
	f := &Funcao{}
	f.Emitir(OpConst, 0, 0, token.Posicao{Linha: 1, Coluna: 1})
	p := &Programa{Principal: f, Constantes: []interp.Valor{interp.Texto("oi")}}
	out := DesmontarFuncao(p, f)
	if !strings.Contains(out, "<anônima>") || !strings.Contains(out, `; "oi"`) {
		t.Errorf("saída inesperada:\n%s", out)
	}
}

func TestValidarDetectaErros(t *testing.T) {
	casos := []struct {
		nome string
		mexe func(p *Programa)
		quer string
	}{
		{"opcode invalido", func(p *Programa) { p.Principal.Codigo[0].Op = Opcode(250) }, "opcode inválido"},
		{"salto fora", func(p *Programa) { p.Principal.Codigo[5].A = 99 }, "destino de salto 99"},
		{"salto negativo", func(p *Programa) { p.Principal.Codigo[5].A = -1 }, "destino de salto -1"},
		{"constante inexistente", func(p *Programa) { p.Principal.Codigo[3].A = 7 }, "constante 7 inexistente"},
		{"funcao inexistente", func(p *Programa) { p.Principal.Codigo[0].A = 3 }, "função 3 inexistente"},
		{"endereco negativo", func(p *Programa) { p.Principal.Codigo[2].B = -1 }, "endereço de variável negativo"},
		{"chamar negativo", func(p *Programa) { p.Principal.Codigo[4].A = -2 }, "operando negativo"},
		{"posicoes desalinhadas", func(p *Programa) { p.Funcoes[0].Posicoes = p.Funcoes[0].Posicoes[:1] }, "posições para"},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			p := exemplo()
			c.mexe(p)
			err := p.Validar()
			if err == nil || !strings.Contains(err.Error(), c.quer) {
				t.Errorf("erro = %v, quer conter %q", err, c.quer)
			}
		})
	}
}

func TestRemendar(t *testing.T) {
	f := &Funcao{}
	i := f.Emitir(OpSalto, 0, 0, token.Posicao{})
	f.Emitir(OpNulo, 0, 0, token.Posicao{})
	f.Remendar(i, len(f.Codigo))
	if f.Codigo[0].A != 2 {
		t.Errorf("destino = %d, quer 2", f.Codigo[0].A)
	}
}
