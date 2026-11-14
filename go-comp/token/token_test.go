package token

import (
	"errors"
	"testing"
)

func TestBuscarIdent(t *testing.T) {
	casos := []struct {
		entrada string
		quer    Tipo
	}{
		{"let", Let}, {"fn", Fn}, {"if", Se}, {"else", Senao}, {"while", Enquanto},
		{"return", Retorna}, {"true", Verdadeiro}, {"false", Falso},
		{"letra", Ident}, {"x", Ident}, {"Let", Ident}, {"", Ident},
	}
	for _, c := range casos {
		if got := BuscarIdent(c.entrada); got != c.quer {
			t.Errorf("BuscarIdent(%q) = %v, quer %v", c.entrada, got, c.quer)
		}
	}
}

func TestTipoString(t *testing.T) {
	casos := map[Tipo]string{
		Mais: "+", MenorIgual: "<=", Let: "let", FimArquivo: "FIM", Tipo(999): "Tipo(999)", Tipo(-1): "Tipo(-1)",
	}
	for tipo, quer := range casos {
		if got := tipo.String(); got != quer {
			t.Errorf("%d.String() = %q, quer %q", int(tipo), got, quer)
		}
	}
}

func TestPosicao(t *testing.T) {
	p := Posicao{Linha: 3, Coluna: 7}
	if p.String() != "3:7" || !p.Valida() {
		t.Errorf("posição inesperada: %v", p)
	}
	if (Posicao{}).Valida() {
		t.Error("posição zero não deveria ser válida")
	}
}

func TestErro(t *testing.T) {
	casos := []struct {
		err       *Erro
		texto, ms string
	}{
		{Errorf(Posicao{Linha: 2, Coluna: 5}, "esperado %q", ")"), `2:5: esperado ")"`, `esperado ")"`},
		{&Erro{Msg: "sem posição"}, "sem posição", "sem posição"},
	}
	for _, c := range casos {
		if c.err.Error() != c.texto {
			t.Errorf("Error() = %q, quer %q", c.err.Error(), c.texto)
		}
		if c.err.Mensagem() != c.ms {
			t.Errorf("Mensagem() = %q, quer %q", c.err.Mensagem(), c.ms)
		}
	}
	var err error = Errorf(Posicao{Linha: 1, Coluna: 1}, "x")
	var alvo *Erro
	if !errors.As(err, &alvo) || alvo.Pos().Linha != 1 {
		t.Error("errors.As deveria extrair *Erro")
	}
}
