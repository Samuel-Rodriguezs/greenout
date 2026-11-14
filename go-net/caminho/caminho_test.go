package caminho

import (
	"errors"
	"reflect"
	"testing"
)

// Topologia clássica (Dijkstra/Wikipédia, com letras): custos
// A-B 7, A-C 9, A-F 14, B-C 10, B-D 15, C-D 11, C-F 2, D-E 6, E-F 9.
func classica(t *testing.T) *Topologia {
	t.Helper()
	top := Nova()
	for _, e := range []struct {
		a, b  string
		custo int
	}{{"A", "B", 7}, {"A", "C", 9}, {"A", "F", 14}, {"B", "C", 10}, {"B", "D", 15},
		{"C", "D", 11}, {"C", "F", 2}, {"D", "E", 6}, {"E", "F", 9}} {
		if err := top.AdicionarEnlace(e.a, e.b, e.custo); err != nil {
			t.Fatal(err)
		}
	}
	return top
}

func TestCaminhosMinimos(t *testing.T) {
	top := classica(t)
	casos := []struct {
		dest  string
		custo int
		rota  []string
	}{
		{"A", 0, []string{"A"}},
		{"B", 7, []string{"A", "B"}},
		{"C", 9, []string{"A", "C"}},
		{"D", 20, []string{"A", "C", "D"}},
		{"E", 20, []string{"A", "C", "F", "E"}},
		{"F", 11, []string{"A", "C", "F"}},
	}
	for _, c := range casos {
		rota, custo, err := top.CaminhoMinimo("A", c.dest)
		if err != nil || custo != c.custo || !reflect.DeepEqual(rota, c.rota) {
			t.Errorf("A->%s = %v custo %d err %v; esperava %v custo %d", c.dest, rota, custo, err, c.rota, c.custo)
		}
	}
}

func TestSimetriaEmEnlacesBidirecionais(t *testing.T) {
	top := classica(t)
	for _, par := range [][2]string{{"A", "E"}, {"B", "F"}, {"D", "A"}} {
		_, ida, _ := top.CaminhoMinimo(par[0], par[1])
		_, volta, _ := top.CaminhoMinimo(par[1], par[0])
		if ida != volta {
			t.Errorf("%v: ida %d != volta %d", par, ida, volta)
		}
	}
}

func TestInalcancavelEDesconhecido(t *testing.T) {
	top := classica(t)
	top.AdicionarNo("Z")
	if _, _, err := top.CaminhoMinimo("A", "Z"); !errors.Is(err, ErrSemCaminho) {
		t.Errorf("Z isolado: %v", err)
	}
	if _, _, err := top.CaminhoMinimo("A", "nada"); !errors.Is(err, ErrNoDesconhecido) {
		t.Errorf("destino desconhecido: %v", err)
	}
	if _, _, err := top.CaminhoMinimo("nada", "A"); !errors.Is(err, ErrNoDesconhecido) {
		t.Errorf("origem desconhecida: %v", err)
	}
	if _, err := Nova().MenoresCaminhos("A"); !errors.Is(err, ErrNoDesconhecido) {
		t.Errorf("topologia vazia: %v", err)
	}
}

func TestCustoNegativoRejeitado(t *testing.T) {
	top := Nova()
	if err := top.AdicionarEnlace("A", "B", -1); !errors.Is(err, ErrCustoNegativo) {
		t.Errorf("custo negativo: %v", err)
	}
	if len(top.Nos()) != 0 {
		t.Error("enlace rejeitado não deve criar nós")
	}
}

func TestCustoZeroEEnlaceDirecionado(t *testing.T) {
	top := Nova()
	top.AdicionarEnlaceDirecionado("A", "B", 0)
	top.AdicionarEnlaceDirecionado("B", "C", 5)
	rota, custo, err := top.CaminhoMinimo("A", "C")
	if err != nil || custo != 5 || !reflect.DeepEqual(rota, []string{"A", "B", "C"}) {
		t.Errorf("%v %d %v", rota, custo, err)
	}
	if _, _, err := top.CaminhoMinimo("C", "A"); !errors.Is(err, ErrSemCaminho) {
		t.Errorf("sentido contrário não existe: %v", err)
	}
}

func TestDesempateDeterministico(t *testing.T) {
	// Dois caminhos de custo 2 de S até T: via X ou via Y. Deve escolher X (menor nome).
	for i := 0; i < 20; i++ {
		top := Nova()
		top.AdicionarEnlace("S", "Y", 1)
		top.AdicionarEnlace("S", "X", 1)
		top.AdicionarEnlace("Y", "T", 1)
		top.AdicionarEnlace("X", "T", 1)
		rota, custo, _ := top.CaminhoMinimo("S", "T")
		if custo != 2 || !reflect.DeepEqual(rota, []string{"S", "X", "T"}) {
			t.Fatalf("rota = %v custo %d", rota, custo)
		}
	}
}

func TestRemoverEnlaceMudaRota(t *testing.T) {
	top := classica(t)
	if !top.RemoverEnlace("C", "F") || top.RemoverEnlace("C", "F") {
		t.Fatal("RemoverEnlace")
	}
	rota, custo, err := top.CaminhoMinimo("A", "F")
	if err != nil || custo != 14 || !reflect.DeepEqual(rota, []string{"A", "F"}) {
		t.Errorf("sem C-F: %v %d %v", rota, custo, err)
	}
}

func TestProximoSalto(t *testing.T) {
	arv, err := classica(t).MenoresCaminhos("A")
	if err != nil {
		t.Fatal(err)
	}
	want := map[string]string{"B": "B", "C": "C", "D": "C", "E": "C", "F": "C"}
	if got := arv.ProximoSalto(); !reflect.DeepEqual(got, want) {
		t.Errorf("ProximoSalto = %v", got)
	}
}

func TestNos(t *testing.T) {
	if got := classica(t).Nos(); !reflect.DeepEqual(got, []string{"A", "B", "C", "D", "E", "F"}) {
		t.Errorf("Nos = %v", got)
	}
}

// Anel de n roteadores: o caminho mais curto entre extremos passa pelo lado menor.
func TestAnel(t *testing.T) {
	top := Nova()
	nomes := []string{"r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7"}
	for i := range nomes {
		top.AdicionarEnlace(nomes[i], nomes[(i+1)%len(nomes)], 1)
	}
	_, custo, _ := top.CaminhoMinimo("r0", "r5")
	if custo != 3 {
		t.Errorf("custo r0->r5 = %d, esperava 3", custo)
	}
}
