package validador

import (
	"errors"
	"slices"
	"testing"
)

type endereco struct {
	CEP string `valida:"obrigatorio,min=8,max=9"`
}

type usuario struct {
	Nome   string   `valida:"obrigatorio,min=3,max=10"`
	Email  string   `valida:"email"`
	Idade  int      `valida:"min=18,max=120"`
	Perfil string   `valida:"em=admin|user"`
	Tags   []string `valida:"max=2"`
	Nota   float64  `valida:"min=0.5,max=10"`
	Ender  endereco
	oculto string `valida:"obrigatorio"` // não exportado: ignorado
	Livre  string
}

func regras(t *testing.T, v any) []string {
	t.Helper()
	err := Validar(v)
	if err == nil {
		return nil
	}
	var es Erros
	if !errors.As(err, &es) {
		t.Fatalf("tipo de erro inesperado %T", err)
	}
	r := []string{}
	for _, e := range es {
		r = append(r, e.Campo+":"+e.Regra)
	}
	slices.Sort(r)
	return r
}

func TestValidar(t *testing.T) {
	ok := usuario{Nome: "Maria", Email: "m@x.com", Idade: 30, Perfil: "admin", Tags: []string{"a"}, Nota: 5, Ender: endereco{CEP: "12345678"}}
	casos := []struct {
		nome string
		mut  func(u *usuario)
		want []string
	}{
		{"valido", func(u *usuario) {}, nil},
		{"nome vazio", func(u *usuario) { u.Nome = "" }, []string{"Nome:obrigatorio"}},
		{"nome curto", func(u *usuario) { u.Nome = "ab" }, []string{"Nome:min"}},
		{"nome longo", func(u *usuario) { u.Nome = "abcdefghijk" }, []string{"Nome:max"}},
		{"nome com acento conta runas", func(u *usuario) { u.Nome = "ãéí" }, nil},
		{"email invalido", func(u *usuario) { u.Email = "x@y" }, []string{"Email:email"}},
		{"email vazio opcional", func(u *usuario) { u.Email = "" }, nil},
		{"idade menor", func(u *usuario) { u.Idade = 10 }, []string{"Idade:min"}},
		{"idade maior", func(u *usuario) { u.Idade = 200 }, []string{"Idade:max"}},
		{"idade zero opcional", func(u *usuario) { u.Idade = 0 }, nil},
		{"perfil fora da lista", func(u *usuario) { u.Perfil = "root" }, []string{"Perfil:em"}},
		{"slice grande", func(u *usuario) { u.Tags = []string{"a", "b", "c"} }, []string{"Tags:max"}},
		{"float abaixo", func(u *usuario) { u.Nota = 0.1 }, []string{"Nota:min"}},
		{"aninhado vazio", func(u *usuario) { u.Ender.CEP = "" }, []string{"Ender.CEP:obrigatorio"}},
		{"aninhado curto", func(u *usuario) { u.Ender.CEP = "123" }, []string{"Ender.CEP:min"}},
		{"multiplos", func(u *usuario) { u.Nome = ""; u.Idade = 1; u.Perfil = "x" },
			[]string{"Idade:min", "Nome:obrigatorio", "Perfil:em"}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			u := ok
			c.mut(&u)
			if got := regras(t, u); !slices.Equal(got, c.want) {
				t.Fatalf("got %v want %v", got, c.want)
			}
		})
	}
}

func TestPonteiroENaoStruct(t *testing.T) {
	u := &usuario{Nome: "Maria", Ender: endereco{CEP: "12345678"}}
	if err := Validar(u); err != nil {
		t.Fatalf("ponteiro válido: %v", err)
	}
	if Validar(42) == nil || Validar((*usuario)(nil)) == nil {
		t.Fatal("deveria rejeitar não-struct e ponteiro nulo")
	}
}

func TestTagsInvalidas(t *testing.T) {
	type ruim struct {
		A string `valida:"min=abc"`
		B bool   `valida:"min=1"`
		C string `valida:"inexistente"`
	}
	got := regras(t, ruim{A: "x", B: true, C: "y"})
	want := []string{"A:tag", "B:tag", "C:tag"}
	if !slices.Equal(got, want) {
		t.Fatalf("got %v", got)
	}
}

func TestMensagemDeErro(t *testing.T) {
	err := Validar(usuario{})
	if err == nil || err.Error() == "" {
		t.Fatal("esperava mensagem")
	}
}
