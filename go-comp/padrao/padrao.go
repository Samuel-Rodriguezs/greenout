// Pacote padrao é a biblioteca padrão mínima de Mini: len, print e push.
// As mesmas funções nativas servem ao interpretador e à VM.
package padrao

import (
	"fmt"
	"io"
	"sort"
	"strings"

	"greenout/comp/interp"
	"greenout/comp/tipos"
)

// Embutidos devolve as funções nativas; print escreve em saida.
func Embutidos(saida io.Writer) map[string]*interp.Nativa {
	return map[string]*interp.Nativa{
		"len":   {Nome: "len", Aridade: 1, Fn: tamanho},
		"push":  {Nome: "push", Aridade: 2, Fn: empurrar},
		"print": {Nome: "print", Aridade: -1, Fn: func(args []interp.Valor) (interp.Valor, error) { return imprimir(saida, args) }},
	}
}

// Nomes devolve os nomes dos embutidos em ordem alfabética.
func Nomes() []string {
	ns := make([]string, 0, 3)
	for n := range Embutidos(io.Discard) {
		ns = append(ns, n)
	}
	sort.Strings(ns)
	return ns
}

// Assinaturas devolve os tipos dos embutidos para a verificação de tipos.
func Assinaturas() map[string]*tipos.Assinatura { return tipos.PadraoEmbutidos() }

// Instalar registra os embutidos no interpretador.
func Instalar(in *interp.Interp, saida io.Writer) {
	for nome, nat := range Embutidos(saida) {
		in.DefinirEmbutido(nome, nat)
	}
}

// tamanho implementa len: bytes de um texto ou elementos de um array.
func tamanho(args []interp.Valor) (interp.Valor, error) {
	switch x := args[0].(type) {
	case interp.Texto:
		return interp.Inteiro(len(x)), nil
	case *interp.Array:
		return interp.Inteiro(len(x.Elems)), nil
	}
	return nil, fmt.Errorf("len não aplicável a %s", args[0].Tipo())
}

// empurrar implementa push: acrescenta ao final do array (no lugar) e o devolve.
func empurrar(args []interp.Valor) (interp.Valor, error) {
	arr, ok := args[0].(*interp.Array)
	if !ok {
		return nil, fmt.Errorf("push requer array como primeiro argumento, recebeu %s", args[0].Tipo())
	}
	arr.Elems = append(arr.Elems, args[1])
	return arr, nil
}

// imprimir implementa print: valores separados por espaço e quebra de linha.
// Textos aparecem sem aspas no nível superior e entre aspas dentro de arrays.
func imprimir(saida io.Writer, args []interp.Valor) (interp.Valor, error) {
	partes := make([]string, len(args))
	for i, a := range args {
		partes[i] = a.String()
	}
	if _, err := io.WriteString(saida, strings.Join(partes, " ")+"\n"); err != nil {
		return nil, fmt.Errorf("print: %v", err)
	}
	return interp.Nulo{}, nil
}
