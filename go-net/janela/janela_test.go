package janela

import (
	"errors"
	"reflect"
	"testing"
)

type simulador func(total, janela int, c *Canal) (Resultado, error)

var protocolos = map[string]simulador{"GoBackN": GoBackN, "SelectiveRepeat": SelectiveRepeat}

func sequencia(n int) []int {
	s := make([]int, n)
	for i := range s {
		s[i] = i
	}
	return s
}

func TestSemPerda(t *testing.T) {
	casos := []struct {
		total, janela, rodadas int
	}{
		{0, 4, 0},
		{1, 4, 1},
		{10, 4, 3},
		{12, 4, 3},
		{10, 1, 10},
		{5, 100, 1},
	}
	for nome, sim := range protocolos {
		for _, c := range casos {
			r, err := sim(c.total, c.janela, NovoCanal(1, 0))
			if err != nil {
				t.Fatalf("%s: %v", nome, err)
			}
			if r.Rodadas != c.rodadas || r.Transmissoes != c.total || !reflect.DeepEqual(r.Entregues, append([]int(nil), sequencia(c.total)...)) && c.total > 0 {
				t.Errorf("%s total=%d janela=%d: %+v", nome, c.total, c.janela, r)
			}
		}
	}
}

func TestEntregaCompletaEmOrdemComPerda(t *testing.T) {
	for nome, sim := range protocolos {
		for _, perda := range []int{10, 30, 60} {
			for seed := int64(1); seed <= 5; seed++ {
				canal := NovoCanal(seed, perda)
				r, err := sim(50, 8, canal)
				if err != nil {
					t.Fatalf("%s perda=%d seed=%d: %v", nome, perda, seed, err)
				}
				if !reflect.DeepEqual(r.Entregues, sequencia(50)) {
					t.Fatalf("%s perda=%d seed=%d: entrega fora de ordem ou incompleta: %v", nome, perda, seed, r.Entregues)
				}
				if r.Transmissoes < 50 {
					t.Errorf("%s: transmissões %d < 50", nome, r.Transmissoes)
				}
				if canal.Perdidos == 0 {
					t.Errorf("%s perda=%d seed=%d: esperava alguma perda", nome, perda, seed)
				}
			}
		}
	}
}

func TestDeterminismoPorSemente(t *testing.T) {
	for nome, sim := range protocolos {
		a, _ := sim(40, 5, NovoCanal(42, 25))
		b, _ := sim(40, 5, NovoCanal(42, 25))
		if !reflect.DeepEqual(a, b) {
			t.Errorf("%s: mesma semente deu resultados diferentes", nome)
		}
		distintos := map[int]bool{}
		for seed := int64(1); seed <= 10; seed++ {
			r, _ := sim(40, 5, NovoCanal(seed, 25))
			distintos[r.Transmissoes] = true
		}
		if len(distintos) < 2 {
			t.Errorf("%s: sementes diferentes deveriam variar o resultado", nome)
		}
	}
}

// Em média o Selective Repeat retransmite menos que o Go-Back-N.
func TestSelectiveRepeatTransmiteMenosEmMedia(t *testing.T) {
	var gbn, sr int
	for seed := int64(1); seed <= 40; seed++ {
		a, _ := GoBackN(100, 10, NovoCanal(seed, 20))
		b, _ := SelectiveRepeat(100, 10, NovoCanal(seed, 20))
		gbn += a.Transmissoes
		sr += b.Transmissoes
	}
	if sr >= gbn {
		t.Errorf("SR=%d deveria transmitir menos que GBN=%d", sr, gbn)
	}
}

func TestParametrosInvalidos(t *testing.T) {
	for nome, sim := range protocolos {
		if _, err := sim(-1, 4, NovoCanal(1, 0)); !errors.Is(err, ErrParametros) {
			t.Errorf("%s total negativo: %v", nome, err)
		}
		if _, err := sim(5, 0, NovoCanal(1, 0)); !errors.Is(err, ErrParametros) {
			t.Errorf("%s janela 0: %v", nome, err)
		}
		if _, err := sim(5, 4, nil); !errors.Is(err, ErrParametros) {
			t.Errorf("%s canal nulo: %v", nome, err)
		}
		if _, err := sim(5, 4, NovoCanal(1, 101)); !errors.Is(err, ErrParametros) {
			t.Errorf("%s perda 101: %v", nome, err)
		}
	}
}

func TestPerdaTotalNaoConclui(t *testing.T) {
	for nome, sim := range protocolos {
		if _, err := sim(3, 2, NovoCanal(1, 100)); !errors.Is(err, ErrSemProgresso) {
			t.Errorf("%s com 100%% de perda: %v", nome, err)
		}
	}
}

func TestCanalContabiliza(t *testing.T) {
	c := NovoCanal(7, 50)
	entregues := 0
	for i := 0; i < 1000; i++ {
		if c.Entrega() {
			entregues++
		}
	}
	if c.Enviados != 1000 || c.Perdidos != 1000-entregues {
		t.Errorf("contadores: %d %d %d", c.Enviados, c.Perdidos, entregues)
	}
	if entregues < 400 || entregues > 600 {
		t.Errorf("perda de 50%% deu %d entregas em 1000", entregues)
	}
}
