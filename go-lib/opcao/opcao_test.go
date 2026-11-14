package opcao

import (
	"errors"
	"strconv"
	"testing"
)

func TestOpcao(t *testing.T) {
	casos := []struct {
		nome string
		o    Opcao[int]
		tem  bool
		v    int
		ou   int
	}{
		{"algum", Algum(5), true, 5, 5},
		{"algum zero", Algum(0), true, 0, 0},
		{"nenhum", Nenhum[int](), false, 0, 9},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			v, ok := c.o.Valor()
			if c.o.TemValor() != c.tem || ok != c.tem || v != c.v {
				t.Fatalf("estado errado: %v %v", v, ok)
			}
			if got := c.o.ValorOu(9); got != c.ou {
				t.Fatalf("ValorOu %d", got)
			}
		})
	}
}

func TestMapearOpcao(t *testing.T) {
	if v, ok := MapearOpcao(Algum(2), strconv.Itoa).Valor(); !ok || v != "2" {
		t.Fatal("mapear algum")
	}
	if MapearOpcao(Nenhum[int](), strconv.Itoa).TemValor() {
		t.Fatal("mapear nenhum")
	}
}

func TestResultado(t *testing.T) {
	boom := errors.New("boom")
	if !Ok(1).EhOk() || Falha[int](boom).EhOk() {
		t.Fatal("EhOk")
	}
	if _, err := Falha[int](boom).Desempacotar(); !errors.Is(err, boom) {
		t.Fatal("erro deve ser preservado")
	}
	if Falha[int](nil).EhOk() {
		t.Fatal("Falha(nil) não pode ser Ok")
	}
	if Falha[int](boom).ValorOu(7) != 7 || Ok(3).ValorOu(7) != 3 {
		t.Fatal("ValorOu")
	}
	if !De(1, nil).EhOk() || De(0, boom).EhOk() {
		t.Fatal("De")
	}
}

func TestEncadear(t *testing.T) {
	analisa := func(s string) Resultado[int] { return De(strconv.Atoi(s)) }
	dobra := func(n int) Resultado[int] { return Ok(n * 2) }
	r := EncadearResultado(analisa("21"), dobra)
	if v, err := r.Desempacotar(); err != nil || v != 42 {
		t.Fatalf("got %v %v", v, err)
	}
	if EncadearResultado(analisa("x"), dobra).EhOk() {
		t.Fatal("erro deve propagar")
	}
	if MapearResultado(analisa("x"), func(n int) int { return n }).EhOk() {
		t.Fatal("mapear deve propagar erro")
	}
	if v, _ := MapearResultado(Ok(2), func(n int) string { return strconv.Itoa(n + 1) }).Desempacotar(); v != "3" {
		t.Fatal("mapear ok")
	}
}
