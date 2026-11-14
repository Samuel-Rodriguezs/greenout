package debounce

import (
	"testing"
	"time"
)

type relogio struct{ t time.Time }

func (r *relogio) Agora() time.Time        { return r.t }
func (r *relogio) Avancar(d time.Duration) { r.t = r.t.Add(d) }
func novo() *relogio                       { return &relogio{t: time.Date(2026, 1, 1, 0, 0, 0, 0, time.UTC)} }

func TestDebounce(t *testing.T) {
	type passo struct {
		avanca   time.Duration
		registra bool
		pronto   bool
	}
	casos := []struct {
		nome   string
		passos []passo
	}{
		{"sem eventos nunca dispara", []passo{{time.Hour, false, false}}},
		{"dispara depois da espera", []passo{
			{0, true, false},
			{99 * time.Millisecond, false, false},
			{time.Millisecond, false, true}, // exatamente 100ms
			{time.Hour, false, false},       // só dispara uma vez
		}},
		{"novo evento reinicia a contagem", []passo{
			{0, true, false},
			{80 * time.Millisecond, true, false},
			{80 * time.Millisecond, false, false},
			{20 * time.Millisecond, false, true},
		}},
		{"nova rajada depois de disparar", []passo{
			{0, true, false},
			{time.Second, false, true},
			{0, true, false},
			{time.Second, false, true},
		}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			r := novo()
			d := NovoDebounce(100*time.Millisecond, r.Agora)
			for i, p := range c.passos {
				r.Avancar(p.avanca)
				if p.registra {
					d.Registrar()
				}
				if got := d.Pronto(); got != p.pronto {
					t.Fatalf("passo %d: Pronto=%v", i, got)
				}
			}
		})
	}
}

func TestThrottle(t *testing.T) {
	r := novo()
	th := NovoThrottle(time.Second, r.Agora)
	passos := []struct {
		avanca time.Duration
		want   bool
	}{
		{0, true},
		{0, false},
		{999 * time.Millisecond, false},
		{time.Millisecond, true},
		{500 * time.Millisecond, false},
		{500 * time.Millisecond, true},
	}
	for i, p := range passos {
		r.Avancar(p.avanca)
		if got := th.Permitir(); got != p.want {
			t.Fatalf("passo %d: got %v", i, got)
		}
	}
}

func TestRelogioPadrao(t *testing.T) {
	if !NovoThrottle(time.Hour, nil).Permitir() {
		t.Fatal("primeira chamada deve passar")
	}
	d := NovoDebounce(time.Hour, nil)
	d.Registrar()
	if d.Pronto() {
		t.Fatal("não deveria estar pronto")
	}
}
