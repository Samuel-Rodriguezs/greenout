package kvttl

import (
	"testing"
	"time"
)

type relogio struct{ t time.Time }

func (r *relogio) agora() time.Time        { return r.t }
func (r *relogio) avancar(d time.Duration) { r.t = r.t.Add(d) }

func novoStore() (*Store, *relogio) {
	r := &relogio{t: time.Date(2026, 1, 1, 0, 0, 0, 0, time.UTC)}
	return Novo(r.agora), r
}

func TestExpiracao(t *testing.T) {
	casos := []struct {
		nome     string
		ttl      time.Duration
		avanco   time.Duration
		esperaOK bool
	}{
		{"antes de expirar", 10 * time.Second, 9 * time.Second, true},
		{"no instante exato", 10 * time.Second, 10 * time.Second, false},
		{"depois de expirar", 10 * time.Second, time.Minute, false},
		{"sem ttl", 0, 24 * time.Hour, true},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			s, r := novoStore()
			s.Definir("k", "v", c.ttl)
			r.avancar(c.avanco)
			v, ok := s.Obter("k")
			if ok != c.esperaOK || (ok && v != "v") {
				t.Errorf("Obter = %q, %v", v, ok)
			}
		})
	}
}

func TestSobrescreverERemover(t *testing.T) {
	s, r := novoStore()
	s.Definir("k", "1", time.Second)
	s.Definir("k", "2", time.Hour)
	r.avancar(time.Minute)
	if v, ok := s.Obter("k"); !ok || v != "2" {
		t.Errorf("Obter = %q, %v", v, ok)
	}
	if !s.Remover("k") {
		t.Error("Remover deveria retornar true")
	}
	if s.Remover("k") {
		t.Error("segunda remoção deveria retornar false")
	}
}

func TestTTLRestanteELimpar(t *testing.T) {
	s, r := novoStore()
	s.Definir("a", "1", 10*time.Second)
	s.Definir("b", "2", 0)
	s.Definir("c", "3", 5*time.Second)
	r.avancar(6 * time.Second)

	if d, ok := s.TTLRestante("a"); !ok || d != 4*time.Second {
		t.Errorf("TTLRestante(a) = %v, %v", d, ok)
	}
	if d, ok := s.TTLRestante("b"); !ok || d != 0 {
		t.Errorf("TTLRestante(b) = %v, %v", d, ok)
	}
	if _, ok := s.TTLRestante("c"); ok {
		t.Error("c deveria ter expirado")
	}
	if _, ok := s.TTLRestante("zzz"); ok {
		t.Error("chave inexistente")
	}
	if n := s.Limpar(); n != 1 {
		t.Errorf("Limpar removeu %d, esperado 1", n)
	}
	if s.Tamanho() != 2 {
		t.Errorf("Tamanho = %d, esperado 2", s.Tamanho())
	}
}

func TestRelogioPadrao(t *testing.T) {
	s := Novo(nil)
	s.Definir("k", "v", time.Hour)
	if _, ok := s.Obter("k"); !ok {
		t.Error("esperava encontrar a chave")
	}
}
