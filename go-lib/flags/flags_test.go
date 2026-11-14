package flags

import (
	"slices"
	"strings"
	"testing"
	"time"
)

type alvo struct {
	nome    *string
	n       *int
	v       *bool
	d       *time.Duration
	conjunt *Conjunto
}

func novoAlvo() alvo {
	c := Novo("prog")
	return alvo{
		nome:    c.Texto("nome", 'n', "mundo", "nome"),
		n:       c.Inteiro("vezes", 'x', 1, "repetições"),
		v:       c.Bool("verboso", 'v', false, "detalhado"),
		d:       c.Duracao("tempo", 't', time.Second, "espera"),
		conjunt: c,
	}
}

func TestParse(t *testing.T) {
	casos := []struct {
		nome string
		args []string
		erro string
		nm   string
		n    int
		v    bool
		d    time.Duration
		pos  []string
	}{
		{"padroes", nil, "", "mundo", 1, false, time.Second, nil},
		{"longa com igual", []string{"--nome=ana", "--vezes=3"}, "", "ana", 3, false, time.Second, nil},
		{"longa com espaco", []string{"--nome", "ana", "--vezes", "3"}, "", "ana", 3, false, time.Second, nil},
		{"curta", []string{"-n", "bia", "-x", "7", "-v"}, "", "bia", 7, true, time.Second, nil},
		{"curta com igual", []string{"-n=bia"}, "", "bia", 1, false, time.Second, nil},
		{"bool explicito falso", []string{"-v", "--verboso=false"}, "", "mundo", 1, false, time.Second, nil},
		{"bool nao consome proximo", []string{"-v", "arquivo"}, "", "mundo", 1, true, time.Second, []string{"arquivo"}},
		{"duracao", []string{"--tempo=1m30s"}, "", "mundo", 1, false, 90 * time.Second, nil},
		{"posicionais intercalados", []string{"a", "-x", "2", "b", "-", "c"}, "", "mundo", 2, false, time.Second, []string{"a", "b", "-", "c"}},
		{"terminador", []string{"-x", "2", "--", "--nome", "-v"}, "", "mundo", 2, false, time.Second, []string{"--nome", "-v"}},
		{"valor com igual", []string{"--nome=a=b"}, "", "a=b", 1, false, time.Second, nil},
		{"valor negativo", []string{"-x", "-5"}, "", "mundo", -5, false, time.Second, nil},
		{"desconhecida", []string{"--nada"}, "desconhecida", "", 0, false, 0, nil},
		{"curta desconhecida", []string{"-z"}, "desconhecida", "", 0, false, 0, nil},
		{"falta valor", []string{"--nome"}, "requer um valor", "", 0, false, 0, nil},
		{"int invalido", []string{"--vezes=abc"}, "inteiro inválido", "", 0, false, 0, nil},
		{"bool invalido", []string{"--verboso=talvez"}, "booleano inválido", "", 0, false, 0, nil},
		{"duracao invalida", []string{"--tempo=xx"}, "duração inválida", "", 0, false, 0, nil},
		{"curta agrupada rejeitada", []string{"-vx"}, "flag curta inválida", "", 0, false, 0, nil},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			a := novoAlvo()
			err := a.conjunt.Parse(c.args)
			if c.erro != "" {
				if err == nil || !strings.Contains(err.Error(), c.erro) {
					t.Fatalf("erro %v, esperava conter %q", err, c.erro)
				}
				return
			}
			if err != nil {
				t.Fatal(err)
			}
			if *a.nome != c.nm || *a.n != c.n || *a.v != c.v || *a.d != c.d {
				t.Fatalf("valores: %q %d %v %v", *a.nome, *a.n, *a.v, *a.d)
			}
			if !slices.Equal(a.conjunt.Posicionais(), c.pos) {
				t.Fatalf("posicionais %v", a.conjunt.Posicionais())
			}
		})
	}
}

func TestParseReinicia(t *testing.T) {
	a := novoAlvo()
	a.conjunt.Parse([]string{"x"})
	a.conjunt.Parse([]string{"y"})
	if !slices.Equal(a.conjunt.Posicionais(), []string{"y"}) {
		t.Fatal("posicionais devem ser reiniciados a cada Parse")
	}
}

func TestDuplicadaPanic(t *testing.T) {
	casos := map[string]func(c *Conjunto){
		"nome":  func(c *Conjunto) { c.Bool("a", 0, false, ""); c.Bool("a", 0, false, "") },
		"curto": func(c *Conjunto) { c.Bool("a", 'x', false, ""); c.Bool("b", 'x', false, "") },
	}
	for nome, f := range casos {
		t.Run(nome, func(t *testing.T) {
			defer func() {
				if recover() == nil {
					t.Fatal("esperava panic")
				}
			}()
			f(Novo("p"))
		})
	}
}

func TestUso(t *testing.T) {
	u := novoAlvo().conjunt.Uso()
	for _, parte := range []string{"Uso: prog", "-n, --nome", "-x, --vezes", "(padrão: mundo)", "(padrão: 1s)"} {
		if !strings.Contains(u, parte) {
			t.Errorf("uso sem %q:\n%s", parte, u)
		}
	}
	c := Novo("p")
	c.Bool("sem-atalho", 0, true, "x")
	if !strings.Contains(c.Uso(), "      --sem-atalho") {
		t.Error("flag sem atalho mal formatada")
	}
}
