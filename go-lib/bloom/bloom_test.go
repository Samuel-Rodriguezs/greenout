package bloom

import (
	"fmt"
	"testing"
)

func TestSemFalsoNegativo(t *testing.T) {
	f := Novo(1000, 0.01)
	for i := 0; i < 1000; i++ {
		f.AdicionarTexto(fmt.Sprintf("item-%d", i))
	}
	for i := 0; i < 1000; i++ {
		if !f.TalvezTexto(fmt.Sprintf("item-%d", i)) {
			t.Fatalf("falso negativo para item-%d", i)
		}
	}
	if f.Adicionados() != 1000 {
		t.Fatalf("adicionados %d", f.Adicionados())
	}
}

func TestTaxaDeFalsoPositivo(t *testing.T) {
	casos := []struct {
		nome string
		taxa float64
	}{
		{"1 por cento", 0.01},
		{"10 por cento", 0.10},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			const n = 2000
			f := Novo(n, c.taxa)
			for i := 0; i < n; i++ {
				f.AdicionarTexto(fmt.Sprintf("dentro-%d", i))
			}
			fp := 0
			const testes = 20000
			for i := 0; i < testes; i++ {
				if f.TalvezTexto(fmt.Sprintf("fora-%d", i)) {
					fp++
				}
			}
			obtida := float64(fp) / testes
			if obtida > c.taxa*2.5 { // margem para variação estatística
				t.Fatalf("taxa %.4f muito acima da alvo %.2f", obtida, c.taxa)
			}
		})
	}
}

func TestVazioENormalizacao(t *testing.T) {
	casos := []struct {
		nome     string
		esperado int
		taxa     float64
	}{
		{"esperados zero", 0, 0.01},
		{"taxa zero", 10, 0},
		{"taxa um", 10, 1},
		{"taxa negativa", 10, -1},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			f := Novo(c.esperado, c.taxa)
			bits, k := f.Parametros()
			if bits < 64 || k < 1 {
				t.Fatalf("parâmetros inválidos: %d %d", bits, k)
			}
			if f.TalvezTexto("qualquer") {
				t.Fatal("filtro vazio não deve conter nada")
			}
			f.Adicionar(nil) // dado vazio é válido
			if !f.Talvez([]byte{}) {
				t.Fatal("dado vazio deveria ser encontrado")
			}
		})
	}
}
