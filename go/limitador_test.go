package lab

import (
	"testing"
	"time"
)

func TestLimitadorTaxa(t *testing.T) {
	agora := time.Date(2026, 1, 1, 0, 0, 0, 0, time.UTC)
	relogio := func() time.Time { return agora }
	l := NovoLimitadorTaxa(3, 1, relogio) // 3 de rajada, 1 token/s

	for i := 0; i < 3; i++ {
		if !l.Permitir() {
			t.Fatalf("rajada %d deveria passar", i)
		}
	}
	if l.Permitir() {
		t.Fatal("quarta deveria ser negada")
	}
	agora = agora.Add(500 * time.Millisecond)
	if l.Permitir() {
		t.Fatal("0,5 token não basta")
	}
	agora = agora.Add(500 * time.Millisecond)
	if !l.Permitir() {
		t.Fatal("após 1s deveria liberar um")
	}
	if l.Permitir() {
		t.Fatal("deveria estar vazio de novo")
	}
	agora = agora.Add(time.Hour) // não passa da capacidade
	for i := 0; i < 3; i++ {
		if !l.Permitir() {
			t.Fatalf("recarga %d deveria passar", i)
		}
	}
	if l.Permitir() {
		t.Fatal("capacidade excedida")
	}
}

func TestLimitadorTaxaParametrosInvalidos(t *testing.T) {
	agora := time.Unix(0, 0)
	l := NovoLimitadorTaxa(0, -5, func() time.Time { return agora })
	if !l.Permitir() {
		t.Fatal("capacidade mínima 1 deveria permitir a primeira")
	}
	agora = agora.Add(time.Hour)
	if l.Permitir() {
		t.Fatal("taxa zero não repõe tokens")
	}
}

func TestLimitadorTaxaRelogioPadrao(t *testing.T) {
	l := NovoLimitadorTaxa(1, 0, nil)
	if !l.Permitir() || l.Permitir() {
		t.Fatal("comportamento inesperado com time.Now")
	}
}
