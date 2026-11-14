// Pacote e2e monta o pipeline completo de Mini (parser, semântica, tipos,
// otimizações, interpretador ou compilador+VM) para que os testes de ponta
// a ponta possam comparar os dois executores sobre os mesmos programas.
package e2e

import (
	"strings"

	"greenout/comp/ast"
	"greenout/comp/compilador"
	"greenout/comp/dobra"
	"greenout/comp/erros"
	"greenout/comp/interp"
	"greenout/comp/mortos"
	"greenout/comp/padrao"
	"greenout/comp/parser"
	"greenout/comp/semantica"
	"greenout/comp/tipos"
	"greenout/comp/vm"
)

// Falha descreve onde e por que a execução parou.
type Falha struct {
	Fase        erros.Fase
	Err         error  // primeiro erro da fase
	Diagnostico string // relatório formatado com trechos do fonte
}

func (f *Falha) Error() string { return string(f.Fase) + ": " + f.Err.Error() }

// Resultado reúne o que o programa imprimiu e a falha, se houve. A saída
// parcial é preservada quando o erro acontece durante a execução.
type Resultado struct {
	Saida string
	Falha *Falha
}

// Estatisticas conta as otimizações aplicadas.
type Estatisticas struct {
	Dobras    int // expressões constantes calculadas
	Removidos int // comandos mortos eliminados
}

func falhaEm(fonte string, fase erros.Fase, err error, itens []error) *Falha {
	col := erros.Novo(fonte)
	for _, e := range itens {
		col.AdicionarErro(fase, e)
	}
	return &Falha{Fase: fase, Err: err, Diagnostico: col.Formatar()}
}

func comoErros[T error](es []T) []error {
	res := make([]error, len(es))
	for i, e := range es {
		res[i] = e
	}
	return res
}

// Preparar executa as fases estáticas. Se otimizar, aplica dobra de
// constantes e eliminação de código morto depois das verificações.
func Preparar(fonte string, otimizar bool) (*ast.Programa, Estatisticas, *Falha) {
	var est Estatisticas
	prog, es := parser.Analisar(fonte)
	if len(es) > 0 {
		return nil, est, falhaEm(fonte, erros.Sintaxe, es[0], comoErros(es))
	}
	if r := semantica.Analisar(prog, semantica.Opcoes{Embutidos: padrao.Nomes()}); len(r.Erros) > 0 {
		return nil, est, falhaEm(fonte, erros.Semantica, r.Erros[0], comoErros(r.Erros))
	}
	if r := tipos.Verificar(prog, tipos.Opcoes{Embutidos: padrao.Assinaturas()}); len(r.Erros) > 0 {
		return nil, est, falhaEm(fonte, erros.Tipos, r.Erros[0], comoErros(r.Erros))
	}
	if otimizar {
		est.Dobras = dobra.Programa(prog)
		est.Removidos = mortos.Eliminar(prog)
	}
	return prog, est, nil
}

// Executar roda o programa no interpretador (usarVM=false) ou compilado na VM.
func Executar(fonte string, usarVM, otimizar bool) Resultado {
	prog, _, falha := Preparar(fonte, otimizar)
	if falha != nil {
		return Resultado{Falha: falha}
	}
	var saida strings.Builder
	var err error
	if usarVM {
		compilado, cerr := compilador.Compilar(prog, padrao.Nomes())
		if cerr != nil {
			return Resultado{Falha: falhaEm(fonte, erros.Compilacao, cerr, []error{cerr})}
		}
		if verr := compilado.Validar(); verr != nil {
			return Resultado{Falha: falhaEm(fonte, erros.Compilacao, verr, []error{verr})}
		}
		err = vm.Novo(compilado, padrao.Embutidos(&saida)).Executar()
	} else {
		in := interp.Novo()
		padrao.Instalar(in, &saida)
		_, err = in.Executar(prog)
	}
	if err != nil {
		return Resultado{Saida: saida.String(), Falha: falhaEm(fonte, erros.Execucao, err, []error{err})}
	}
	return Resultado{Saida: saida.String()}
}
