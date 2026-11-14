package financiamento

import (
	"errors"
	"math"
	"testing"
)

func proximo(a, b, tol float64) bool { return math.Abs(a-b) <= tol }

func TestPrice(t *testing.T) {
	// 10.000 a 1% a.m. em 12 meses: PMT = 888,49
	plano, err := Price(10000, 0.01, 12)
	if err != nil {
		t.Fatal(err)
	}
	if len(plano) != 12 {
		t.Fatalf("len = %d", len(plano))
	}
	if plano[0].Valor != 888.49 || plano[0].Juros != 100 || plano[0].Amortizacao != 788.49 {
		t.Errorf("primeira parcela = %+v", plano[0])
	}
	for _, p := range plano {
		if p.Valor != 888.49 {
			t.Errorf("parcela %d = %v, esperava valor fixo", p.Numero, p.Valor)
		}
	}
	if ultimo := plano[11]; ultimo.Saldo != 0 {
		t.Errorf("saldo final = %v", ultimo.Saldo)
	}
	if !proximo(TotalPago(plano), 10661.85, 0.2) {
		t.Errorf("total pago = %v", TotalPago(plano))
	}
}

func TestSAC(t *testing.T) {
	plano, err := SAC(12000, 0.01, 12)
	if err != nil {
		t.Fatal(err)
	}
	// amortização 1000; juros 120 -> parcela 1120; última: 1000 + 10 = 1010
	if plano[0].Valor != 1120 || plano[0].Juros != 120 || plano[0].Amortizacao != 1000 {
		t.Errorf("primeira = %+v", plano[0])
	}
	if plano[11].Valor != 1010 || plano[11].Saldo != 0 {
		t.Errorf("última = %+v", plano[11])
	}
	for i := 1; i < len(plano); i++ {
		if plano[i].Valor >= plano[i-1].Valor {
			t.Errorf("parcelas deveriam decrescer: %v >= %v", plano[i].Valor, plano[i-1].Valor)
		}
	}
	if TotalJuros(plano) != 780 { // 1% * 1000 * (12+11+...+1)
		t.Errorf("juros totais = %v", TotalJuros(plano))
	}
}

func TestTaxaZero(t *testing.T) {
	plano, err := Price(1200, 0, 4)
	if err != nil {
		t.Fatal(err)
	}
	for _, p := range plano {
		if p.Valor != 300 || p.Juros != 0 {
			t.Errorf("parcela = %+v", p)
		}
	}
}

func TestSACMenosJurosQuePrice(t *testing.T) {
	p, _ := Price(50000, 0.015, 36)
	s, _ := SAC(50000, 0.015, 36)
	if TotalJuros(s) >= TotalJuros(p) {
		t.Errorf("SAC (%v) deveria pagar menos juros que Price (%v)", TotalJuros(s), TotalJuros(p))
	}
}

func TestParametrosInvalidos(t *testing.T) {
	casos := []struct {
		nome      string
		principal float64
		taxa      float64
		n         int
	}{
		{"principal zero", 0, 0.01, 12},
		{"principal negativo", -1, 0.01, 12},
		{"taxa negativa", 100, -0.01, 12},
		{"prazo zero", 100, 0.01, 0},
		{"taxa NaN", 100, math.NaN(), 12},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if _, err := Price(c.principal, c.taxa, c.n); !errors.Is(err, ErrParametros) {
				t.Errorf("Price: erro = %v", err)
			}
			if _, err := SAC(c.principal, c.taxa, c.n); !errors.Is(err, ErrParametros) {
				t.Errorf("SAC: erro = %v", err)
			}
		})
	}
}
