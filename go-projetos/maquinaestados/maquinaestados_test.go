package maquinaestados

import (
	"errors"
	"reflect"
	"testing"
)

func TestFluxoPedido(t *testing.T) {
	casos := []struct {
		nome    string
		eventos []string
		final   string
		falha   bool
	}{
		{"fluxo feliz", []string{"pagar", "enviar", "entregar"}, "entregue", false},
		{"cancelar antes de pagar", []string{"cancelar"}, "cancelado", false},
		{"cancelar pago", []string{"pagar", "cancelar"}, "cancelado", false},
		{"enviar sem pagar", []string{"enviar"}, "criado", true},
		{"cancelar enviado", []string{"pagar", "enviar", "cancelar"}, "enviado", true},
		{"depois de entregue", []string{"pagar", "enviar", "entregar", "pagar"}, "entregue", true},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			m := NovoPedido()
			var err error
			for _, e := range c.eventos {
				if err = m.Disparar(e); err != nil {
					break
				}
			}
			if c.falha != (err != nil) {
				t.Fatalf("erro = %v, falha esperada = %v", err, c.falha)
			}
			if err != nil && !errors.Is(err, ErrTransicaoInvalida) {
				t.Errorf("erro de tipo inesperado: %v", err)
			}
			if m.Estado() != c.final {
				t.Errorf("estado = %q, esperado %q", m.Estado(), c.final)
			}
		})
	}
}

func TestHistoricoECallback(t *testing.T) {
	m := NovoPedido()
	var chamadas []string
	m.AoMudar(func(de, ev, para string) { chamadas = append(chamadas, de+"-"+ev+"->"+para) })
	m.Disparar("pagar")
	m.Disparar("enviar")
	m.Disparar("invalido")

	if want := []string{"criado", "pago", "enviado"}; !reflect.DeepEqual(m.Historico(), want) {
		t.Errorf("historico = %v", m.Historico())
	}
	if want := []string{"criado-pagar->pago", "pago-enviar->enviado"}; !reflect.DeepEqual(chamadas, want) {
		t.Errorf("chamadas = %v", chamadas)
	}
	h := m.Historico()
	h[0] = "alterado"
	if m.Historico()[0] != "criado" {
		t.Error("Historico deve devolver cópia")
	}
}

func TestPode(t *testing.T) {
	m := NovoPedido()
	if !m.Pode("pagar") || m.Pode("enviar") {
		t.Error("Pode retornou valor errado no estado criado")
	}
}
