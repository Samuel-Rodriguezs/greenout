// Pacote financiamento calcula planos de financiamento pelos sistemas
// Price (parcelas fixas) e SAC (amortização constante).
package financiamento

import (
	"errors"
	"math"
)

// ErrParametros indica valores inválidos (principal, taxa ou prazo).
var ErrParametros = errors.New("financiamento: parâmetros inválidos")

// Parcela descreve um pagamento do plano.
type Parcela struct {
	Numero      int
	Valor       float64
	Juros       float64
	Amortizacao float64
	Saldo       float64 // saldo devedor após o pagamento
}

func validar(principal, taxa float64, n int) error {
	if principal <= 0 || taxa < 0 || n <= 0 || math.IsNaN(principal) || math.IsNaN(taxa) {
		return ErrParametros
	}
	return nil
}

func arredondar(v float64) float64 { return math.Round(v*100) / 100 }

// Price gera o plano com parcelas iguais. taxa é mensal (0,02 = 2%).
func Price(principal, taxa float64, n int) ([]Parcela, error) {
	if err := validar(principal, taxa, n); err != nil {
		return nil, err
	}
	pmt := principal / float64(n)
	if taxa > 0 {
		pmt = principal * taxa / (1 - math.Pow(1+taxa, -float64(n)))
	}
	saldo := principal
	plano := make([]Parcela, 0, n)
	for k := 1; k <= n; k++ {
		juros := saldo * taxa
		amort := pmt - juros
		saldo -= amort
		if k == n || saldo < 1e-9 { // elimina resíduo de ponto flutuante
			saldo = 0
		}
		plano = append(plano, Parcela{k, arredondar(pmt), arredondar(juros), arredondar(amort), arredondar(saldo)})
	}
	return plano, nil
}

// SAC gera o plano com amortização constante e parcelas decrescentes.
func SAC(principal, taxa float64, n int) ([]Parcela, error) {
	if err := validar(principal, taxa, n); err != nil {
		return nil, err
	}
	amort := principal / float64(n)
	saldo := principal
	plano := make([]Parcela, 0, n)
	for k := 1; k <= n; k++ {
		juros := saldo * taxa
		saldo -= amort
		if k == n {
			saldo = 0
		}
		plano = append(plano, Parcela{k, arredondar(amort + juros), arredondar(juros), arredondar(amort), arredondar(saldo)})
	}
	return plano, nil
}

// TotalPago soma o valor de todas as parcelas.
func TotalPago(plano []Parcela) float64 {
	t := 0.0
	for _, p := range plano {
		t += p.Valor
	}
	return arredondar(t)
}

// TotalJuros soma os juros de todas as parcelas.
func TotalJuros(plano []Parcela) float64 {
	t := 0.0
	for _, p := range plano {
		t += p.Juros
	}
	return arredondar(t)
}
