package bench

import (
	"strings"
	"testing"
	"time"
)

func TestProgramasProduzemSaidaEsperada(t *testing.T) {
	for _, p := range Programas() {
		t.Run(p.Nome, func(t *testing.T) {
			saida, err := RodarInterp(p.Fonte)
			if err != nil || saida != p.Esperado {
				t.Errorf("interp: saída %q err %v, quer %q", saida, err, p.Esperado)
			}
			bc, err := Compilar(p.Fonte)
			if err != nil {
				t.Fatal(err)
			}
			saida, err = RodarVM(bc)
			if err != nil || saida != p.Esperado {
				t.Errorf("vm: saída %q err %v, quer %q", saida, err, p.Esperado)
			}
		})
	}
}

func TestComparar(t *testing.T) {
	for _, p := range Programas() {
		m, err := Comparar(p, 2)
		if err != nil {
			t.Errorf("%s: %v", p.Nome, err)
			continue
		}
		if m.Interp <= 0 || m.VM <= 0 || m.Razao() <= 0 {
			t.Errorf("%s: medidas inválidas %+v", p.Nome, m)
		}
		if !strings.Contains(m.String(), p.Nome) {
			t.Errorf("String() sem nome: %s", m)
		}
	}
}

func TestCompararDetectaSaidaErrada(t *testing.T) {
	p := Programa{Nome: "errado", Fonte: "print(1);", Esperado: "2\n"}
	if _, err := Comparar(p, 1); err == nil || !strings.Contains(err.Error(), "esperado") {
		t.Errorf("erro = %v", err)
	}
	if _, err := Comparar(Programa{Nome: "sintaxe", Fonte: "let = ;"}, 1); err == nil {
		t.Error("esperado erro de sintaxe")
	}
	if _, err := Comparar(Programa{Nome: "execucao", Fonte: "print(1 / 0);"}, 1); err == nil {
		t.Error("esperado erro de execução")
	}
}

func TestRazao(t *testing.T) {
	casos := []struct {
		m    Medida
		quer float64
	}{
		{Medida{Interp: 4 * time.Millisecond, VM: 2 * time.Millisecond}, 2},
		{Medida{Interp: time.Millisecond, VM: 2 * time.Millisecond}, 0.5},
		{Medida{Interp: time.Millisecond}, 0},
	}
	for _, c := range casos {
		if got := c.m.Razao(); got != c.quer {
			t.Errorf("Razao(%+v) = %v, quer %v", c.m, got, c.quer)
		}
	}
}

func BenchmarkInterp(b *testing.B) {
	for _, p := range Programas() {
		b.Run(p.Nome, func(b *testing.B) {
			for i := 0; i < b.N; i++ {
				if _, err := RodarInterp(p.Fonte); err != nil {
					b.Fatal(err)
				}
			}
		})
	}
}

func BenchmarkVM(b *testing.B) {
	for _, p := range Programas() {
		bc, err := Compilar(p.Fonte)
		if err != nil {
			b.Fatal(err)
		}
		b.Run(p.Nome, func(b *testing.B) {
			for i := 0; i < b.N; i++ {
				if _, err := RodarVM(bc); err != nil {
					b.Fatal(err)
				}
			}
		})
	}
}
