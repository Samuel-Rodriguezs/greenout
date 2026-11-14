package iterador

import (
	"errors"
	"fmt"
	"math/rand"
	"reflect"
	"sort"
	"testing"
)

func es(pares ...string) []Entrada {
	var out []Entrada
	for i := 0; i+1 < len(pares); i += 2 {
		e := Entrada{Chave: pares[i]}
		if pares[i+1] == "-" {
			e.Apagado = true
		} else {
			e.Valor = []byte(pares[i+1])
		}
		out = append(out, e)
	}
	return out
}

func resumo(es []Entrada) []string {
	var r []string
	for _, e := range es {
		if e.Apagado {
			r = append(r, e.Chave+"=-")
		} else {
			r = append(r, e.Chave+"="+string(e.Valor))
		}
	}
	return r
}

func TestDeSlice(t *testing.T) {
	casos := []struct {
		nome string
		in   []Entrada
		quer []string
	}{
		{"nil", nil, nil},
		{"uma", es("a", "1"), []string{"a=1"}},
		{"varias", es("a", "1", "b", "2", "c", "-"), []string{"a=1", "b=2", "c=-"}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			it := DeSlice(c.in)
			got, err := Coletar(it)
			if err != nil || !reflect.DeepEqual(resumo(got), c.quer) {
				t.Fatalf("got %v err %v", resumo(got), err)
			}
			if it.Proximo() {
				t.Fatal("iterador esgotado não deve avançar")
			}
		})
	}
}

func TestMesclar(t *testing.T) {
	casos := []struct {
		nome   string
		fontes [][]Entrada
		quer   []string
	}{
		{"sem fontes", nil, nil},
		{"uma fonte", [][]Entrada{es("a", "1", "b", "2")}, []string{"a=1", "b=2"}},
		{"intercaladas", [][]Entrada{es("a", "1", "c", "3"), es("b", "2", "d", "4")},
			[]string{"a=1", "b=2", "c=3", "d=4"}},
		{"mais recente vence", [][]Entrada{es("a", "novo"), es("a", "velho", "b", "x")},
			[]string{"a=novo", "b=x"}},
		{"lápide sobrepõe valor", [][]Entrada{es("a", "-"), es("a", "velho")}, []string{"a=-"}},
		{"valor sobrepõe lápide", [][]Entrada{es("a", "vivo"), es("a", "-")}, []string{"a=vivo"}},
		{"três fontes mesma chave", [][]Entrada{es("k", "2"), es("k", "1"), es("k", "0")}, []string{"k=2"}},
		{"fonte vazia no meio", [][]Entrada{es("a", "1"), nil, es("b", "2")}, []string{"a=1", "b=2"}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			var its []Iterador
			for _, f := range c.fontes {
				its = append(its, DeSlice(f))
			}
			got, err := Coletar(Mesclar(its...))
			if err != nil || !reflect.DeepEqual(resumo(got), c.quer) {
				t.Fatalf("got %v err %v, quer %v", resumo(got), err, c.quer)
			}
		})
	}
}

func TestMesclarAleatorioContraReferencia(t *testing.T) {
	r := rand.New(rand.NewSource(8))
	for rodada := 0; rodada < 50; rodada++ {
		nf := 1 + r.Intn(6)
		ref := map[string]string{}
		var its []Iterador
		// da fonte mais antiga para a mais nova, para montar a referência
		fontes := make([][]Entrada, nf)
		for f := nf - 1; f >= 0; f-- {
			m := map[string]Entrada{}
			for i := 0; i < r.Intn(40); i++ {
				k := fmt.Sprintf("k%02d", r.Intn(30))
				v := fmt.Sprintf("f%d-%d", f, i)
				m[k] = Entrada{Chave: k, Valor: []byte(v)}
				ref[k] = v
			}
			for _, e := range m {
				fontes[f] = append(fontes[f], e)
			}
			sort.Slice(fontes[f], func(a, b int) bool { return fontes[f][a].Chave < fontes[f][b].Chave })
		}
		for _, f := range fontes {
			its = append(its, DeSlice(f))
		}
		got, err := Coletar(Mesclar(its...))
		if err != nil {
			t.Fatal(err)
		}
		if len(got) != len(ref) {
			t.Fatalf("rodada %d: %d entradas, quer %d", rodada, len(got), len(ref))
		}
		for i, e := range got {
			if i > 0 && got[i-1].Chave >= e.Chave {
				t.Fatalf("rodada %d: fora de ordem", rodada)
			}
			if string(e.Valor) != ref[e.Chave] {
				t.Fatalf("rodada %d: %s = %s, quer %s", rodada, e.Chave, e.Valor, ref[e.Chave])
			}
		}
	}
}

type comErro struct {
	Iterador
	apos int
	n    int
	err  error
}

func (c *comErro) Proximo() bool {
	if c.n >= c.apos {
		return false
	}
	c.n++
	return c.Iterador.Proximo()
}
func (c *comErro) Erro() error {
	if c.n >= c.apos {
		return c.err
	}
	return nil
}

func TestMesclarPropagaErro(t *testing.T) {
	falha := errors.New("disco falhou")
	quebrado := &comErro{Iterador: DeSlice(es("b", "1", "d", "2", "f", "3")), apos: 1, err: falha}
	m := Mesclar(DeSlice(es("a", "1", "c", "2", "e", "3")), quebrado)
	got, err := Coletar(m)
	if err != falha {
		t.Fatalf("err = %v", err)
	}
	if len(got) >= 6 {
		t.Fatalf("deveria ter parado antes do fim: %v", resumo(got))
	}
	if m.Proximo() {
		t.Fatal("depois do erro não deve avançar")
	}
}

func TestIntervalo(t *testing.T) {
	base := es("a", "1", "b", "2", "c", "3", "d", "4", "e", "5")
	casos := []struct {
		nome      string
		de, ate   string
		ilimitado bool
		quer      []string
	}{
		{"meio", "b", "d", false, []string{"b=2", "c=3"}},
		{"sem limite superior", "c", "", true, []string{"c=3", "d=4", "e=5"}},
		{"vazio", "c", "c", false, nil},
		{"invertido", "d", "b", false, nil},
		{"tudo", "", "", true, []string{"a=1", "b=2", "c=3", "d=4", "e=5"}},
		{"fora", "x", "z", false, nil},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			got, _ := Coletar(Intervalo(DeSlice(base), c.de, c.ate, c.ilimitado))
			if !reflect.DeepEqual(resumo(got), c.quer) {
				t.Fatalf("got %v", resumo(got))
			}
		})
	}
}

func TestLimitarESemApagados(t *testing.T) {
	base := es("a", "1", "b", "-", "c", "3", "d", "-", "e", "5")
	got, _ := Coletar(SemApagados(DeSlice(base)))
	if !reflect.DeepEqual(resumo(got), []string{"a=1", "c=3", "e=5"}) {
		t.Fatalf("sem apagados: %v", resumo(got))
	}
	got, _ = Coletar(Limitar(SemApagados(DeSlice(base)), 2))
	if !reflect.DeepEqual(resumo(got), []string{"a=1", "c=3"}) {
		t.Fatalf("limitar: %v", resumo(got))
	}
	for _, n := range []int{0, -1} {
		got, _ = Coletar(Limitar(DeSlice(base), n))
		if len(got) != 0 {
			t.Fatalf("limite %d devolveu %d entradas", n, len(got))
		}
	}
	got, _ = Coletar(Limitar(DeSlice(base), 100))
	if len(got) != 5 {
		t.Fatalf("limite maior que o total: %d", len(got))
	}
}

func TestComposicaoCompleta(t *testing.T) {
	novo := DeSlice(es("b", "-", "d", "novo-d", "f", "novo-f"))
	velho := DeSlice(es("a", "velho-a", "b", "velho-b", "d", "velho-d", "e", "velho-e"))
	it := Limitar(SemApagados(Intervalo(Mesclar(novo, velho), "b", "f", false)), 10)
	got, err := Coletar(it)
	if err != nil {
		t.Fatal(err)
	}
	if !reflect.DeepEqual(resumo(got), []string{"d=novo-d", "e=velho-e"}) {
		t.Fatalf("got %v", resumo(got))
	}
}
