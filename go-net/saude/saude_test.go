package saude

import (
	"errors"
	"reflect"
	"testing"
	"time"
)

var t0 = time.Date(2026, 1, 1, 0, 0, 0, 0, time.UTC)

// falso devolve falhas conforme o mapa de alvos "fora do ar".
type falso struct {
	fora   map[string]bool
	sondas map[string]int
}

func novoFalso() *falso { return &falso{fora: map[string]bool{}, sondas: map[string]int{}} }

func (f *falso) Verificar(alvo string) error {
	f.sondas[alvo]++
	if f.fora[alvo] {
		return errors.New("fora do ar")
	}
	return nil
}

func TestAlvoSaudavelSondadoPeriodicamente(t *testing.T) {
	f := novoFalso()
	h := Nova(Config{Intervalo: 10 * time.Second}, f)
	h.Adicionar("a", t0)
	if got := h.Executar(t0); !reflect.DeepEqual(got, []string{"a"}) {
		t.Fatalf("primeira sonda: %v", got)
	}
	if got := h.Executar(t0.Add(9 * time.Second)); len(got) != 0 {
		t.Errorf("não deveria sondar antes do intervalo: %v", got)
	}
	if got := h.Executar(t0.Add(10 * time.Second)); len(got) != 1 {
		t.Errorf("deveria sondar aos 10s: %v", got)
	}
	if f.sondas["a"] != 2 {
		t.Errorf("sondas = %d", f.sondas["a"])
	}
}

func TestBackoffExponencialComTeto(t *testing.T) {
	f := novoFalso()
	f.fora["a"] = true
	h := Nova(Config{Intervalo: time.Second, BackoffMax: 10 * time.Second, LimiteFalhas: 3}, f)
	h.Adicionar("a", t0)
	agora := t0
	var intervalos []time.Duration
	for i := 0; i < 6; i++ {
		h.Executar(agora)
		e, _ := h.Estado("a")
		intervalos = append(intervalos, e.Intervalo)
		agora = e.Proxima
	}
	want := []time.Duration{1, 2, 4, 8, 10, 10}
	for i := range want {
		if intervalos[i] != want[i]*time.Second {
			t.Errorf("intervalos = %v, esperava %v s", intervalos, want)
			break
		}
	}
}

func TestLimiarDeQuedaERecuperacao(t *testing.T) {
	f := novoFalso()
	h := Nova(Config{Intervalo: time.Second, LimiteFalhas: 3, LimiteSucessos: 2}, f)
	h.Adicionar("a", t0)
	passo := func(fora bool) Estado {
		f.fora["a"] = fora
		e, _ := h.Estado("a")
		h.Executar(e.Proxima)
		e, _ = h.Estado("a")
		return e
	}
	// Duas falhas ainda não derrubam.
	if e := passo(true); !e.Saudavel || e.Falhas != 1 {
		t.Errorf("1 falha: %+v", e)
	}
	if e := passo(true); !e.Saudavel || e.Falhas != 2 {
		t.Errorf("2 falhas: %+v", e)
	}
	// Um sucesso zera o contador de falhas.
	if e := passo(false); e.Falhas != 0 || e.Sucessos != 1 || !e.Saudavel {
		t.Errorf("sucesso: %+v", e)
	}
	for i := 0; i < 2; i++ {
		passo(true)
	}
	if e := passo(true); e.Saudavel || e.Falhas != 3 {
		t.Errorf("3 falhas seguidas deveriam derrubar: %+v", e)
	}
	if got := h.Saudaveis(); len(got) != 0 {
		t.Errorf("Saudaveis = %v", got)
	}
	// Um sucesso só não basta; dois recuperam.
	if e := passo(false); e.Saudavel || e.Sucessos != 1 {
		t.Errorf("1 sucesso: %+v", e)
	}
	if e := passo(false); !e.Saudavel || e.Sucessos != 2 {
		t.Errorf("2 sucessos: %+v", e)
	}
	if e, _ := h.Estado("a"); e.Intervalo != time.Second {
		t.Errorf("intervalo deveria voltar ao base: %v", e.Intervalo)
	}
}

func TestVariosAlvosIndependentes(t *testing.T) {
	f := novoFalso()
	f.fora["b"] = true
	h := Nova(Config{Intervalo: 5 * time.Second}, f)
	for _, n := range []string{"c", "a", "b"} {
		h.Adicionar(n, t0)
	}
	h.Adicionar("a", t0.Add(time.Hour)) // duplicado ignorado
	if got := h.Executar(t0); !reflect.DeepEqual(got, []string{"a", "b", "c"}) {
		t.Fatalf("ordem de sondagem: %v", got)
	}
	if got := h.Saudaveis(); !reflect.DeepEqual(got, []string{"a", "c"}) {
		t.Errorf("Saudaveis = %v", got)
	}
	// b falhou (intervalo 5s), a e c voltam aos 5s; em 5s todos são devidos.
	if got := h.Executar(t0.Add(5 * time.Second)); len(got) != 3 {
		t.Errorf("sondados em 5s: %v", got)
	}
	// b está com intervalo 10s agora; a e c com 5s.
	if got := h.Executar(t0.Add(10 * time.Second)); !reflect.DeepEqual(got, []string{"a", "c"}) {
		t.Errorf("sondados em 10s: %v", got)
	}
}

func TestRemoverEEstadoDesconhecido(t *testing.T) {
	h := Nova(Config{}, VerificadorFunc(func(string) error { return nil }))
	h.Adicionar("a", t0)
	h.Remover("a")
	if _, ok := h.Estado("a"); ok {
		t.Error("alvo removido")
	}
	if got := h.Executar(t0.Add(time.Hour)); len(got) != 0 {
		t.Errorf("nada a sondar: %v", got)
	}
}

func TestConfigPadrao(t *testing.T) {
	h := Nova(Config{}, VerificadorFunc(func(string) error { return errors.New("x") }))
	h.Adicionar("a", t0)
	h.Executar(t0)
	e, _ := h.Estado("a")
	if e.Saudavel || e.Intervalo != time.Second {
		t.Errorf("padrões: LimiteFalhas=1 e Intervalo=1s, veio %+v", e)
	}
	agora := e.Proxima
	for i := 0; i < 20; i++ {
		h.Executar(agora)
		e, _ = h.Estado("a")
		agora = e.Proxima
	}
	if e.Intervalo != 32*time.Second {
		t.Errorf("teto padrão = 32 x intervalo, veio %v", e.Intervalo)
	}
}
