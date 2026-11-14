package padrao

import (
	"errors"
	"reflect"
	"strings"
	"testing"

	"greenout/comp/compilador"
	"greenout/comp/interp"
	"greenout/comp/parser"
	"greenout/comp/semantica"
	"greenout/comp/tipos"
	"greenout/comp/vm"
)

func TestNomesEAssinaturasConsistentes(t *testing.T) {
	if got, quer := Nomes(), []string{"len", "print", "push"}; !reflect.DeepEqual(got, quer) {
		t.Errorf("Nomes = %v, quer %v", got, quer)
	}
	for _, n := range Nomes() {
		if _, ok := Assinaturas()[n]; !ok {
			t.Errorf("embutido %q sem assinatura de tipos", n)
		}
	}
	if len(Assinaturas()) != len(Nomes()) {
		t.Error("assinaturas e embutidos divergem")
	}
}

func TestFuncoesNativas(t *testing.T) {
	arr := &interp.Array{Elems: []interp.Valor{interp.Inteiro(1)}}
	casos := []struct {
		nome string
		args []interp.Valor
		quer string // String() do resultado
		erro string // trecho esperado do erro
	}{
		{"len texto", []interp.Valor{interp.Texto("olá")}, "4", ""}, // bytes: á ocupa 2
		{"len texto vazio", []interp.Valor{interp.Texto("")}, "0", ""},
		{"len array", []interp.Valor{arr}, "1", ""},
		{"len int", []interp.Valor{interp.Inteiro(3)}, "", "len não aplicável a int"},
		{"len nulo", []interp.Valor{interp.Nulo{}}, "", "len não aplicável a nulo"},
		{"push", []interp.Valor{arr, interp.Texto("x")}, `[1, "x"]`, ""},
		{"push em nao array", []interp.Valor{interp.Texto("a"), interp.Inteiro(1)}, "", "push requer array como primeiro argumento, recebeu texto"},
	}
	nat := Embutidos(&strings.Builder{})
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			nome := strings.Fields(c.nome)[0]
			v, err := nat[nome].Fn(c.args)
			if c.erro != "" {
				if err == nil || !strings.Contains(err.Error(), c.erro) {
					t.Fatalf("erro = %v, quer conter %q", err, c.erro)
				}
				return
			}
			if err != nil {
				t.Fatal(err)
			}
			if v.String() != c.quer {
				t.Errorf("resultado = %s, quer %s", v, c.quer)
			}
		})
	}
	if len(arr.Elems) != 2 {
		t.Error("push deveria modificar o array no lugar")
	}
}

func TestPrint(t *testing.T) {
	casos := []struct {
		nome string
		args []interp.Valor
		quer string
	}{
		{"sem argumentos", nil, "\n"},
		{"varios tipos", []interp.Valor{interp.Inteiro(1), interp.Texto("a"), interp.Booleano(true), interp.Nulo{}}, "1 a true nulo\n"},
		{"array com texto", []interp.Valor{&interp.Array{Elems: []interp.Valor{interp.Texto("a"), interp.Inteiro(2)}}}, "[\"a\", 2]\n"},
	}
	for _, c := range casos {
		var sb strings.Builder
		v, err := Embutidos(&sb)["print"].Fn(c.args)
		if err != nil || v.String() != "nulo" {
			t.Errorf("%s: %v %v", c.nome, v, err)
		}
		if sb.String() != c.quer {
			t.Errorf("%s: saída = %q, quer %q", c.nome, sb.String(), c.quer)
		}
	}
}

type escritorQuebrado struct{}

func (escritorQuebrado) Write([]byte) (int, error) { return 0, errors.New("disco cheio") }

func TestPrintPropagaErroDeEscrita(t *testing.T) {
	_, err := Embutidos(escritorQuebrado{})["print"].Fn([]interp.Valor{interp.Inteiro(1)})
	if err == nil || !strings.Contains(err.Error(), "disco cheio") {
		t.Errorf("erro = %v", err)
	}
}

// O mesmo programa roda no interpretador e na VM usando os embutidos padrão,
// passando antes por semântica e tipos com as mesmas definições.
func TestIntegracao(t *testing.T) {
	fonte := `
let xs = [];
let i = 0;
while (i < 4) { push(xs, i * i); i = i + 1; }
print("xs:", xs, len(xs));
print(len("abc") + len(xs));
`
	prog, erros := parser.Analisar(fonte)
	if len(erros) > 0 {
		t.Fatal(erros)
	}
	if r := semantica.Analisar(prog, semantica.Opcoes{Embutidos: Nomes()}); len(r.Erros) > 0 {
		t.Fatalf("semântica: %v", r.Mensagens())
	}
	if r := tipos.Verificar(prog, tipos.Opcoes{Embutidos: Assinaturas()}); len(r.Erros) > 0 {
		t.Fatalf("tipos: %v", r.Mensagens())
	}
	quer := "xs: [0, 1, 4, 9] 4\n7\n"

	var saidaInterp strings.Builder
	in := interp.Novo()
	Instalar(in, &saidaInterp)
	if _, err := in.Executar(prog); err != nil {
		t.Fatal(err)
	}

	var saidaVM strings.Builder
	p, err := compilador.Compilar(prog, Nomes())
	if err != nil {
		t.Fatal(err)
	}
	if err := vm.Novo(p, Embutidos(&saidaVM)).Executar(); err != nil {
		t.Fatal(err)
	}
	if saidaInterp.String() != quer || saidaVM.String() != quer {
		t.Errorf("interp = %q\nvm = %q\nquer = %q", saidaInterp.String(), saidaVM.String(), quer)
	}
}
