// Pacote maquinaestados implementa uma máquina de estados finita genérica
// e a usa para modelar o ciclo de vida de um pedido.
package maquinaestados

import (
	"errors"
	"fmt"
)

// ErrTransicaoInvalida indica que o evento não é permitido no estado atual.
var ErrTransicaoInvalida = errors.New("maquinaestados: transição inválida")

// Maquina é uma FSM com estados e eventos do tipo string.
type Maquina struct {
	estado     string
	transicoes map[string]map[string]string // estado -> evento -> destino
	aoMudar    func(de, evento, para string)
	historico  []string
}

// Nova cria uma máquina no estado inicial.
func Nova(inicial string) *Maquina {
	return &Maquina{estado: inicial, transicoes: map[string]map[string]string{}, historico: []string{inicial}}
}

// Permitir registra a transição de -> para quando ocorrer o evento.
func (m *Maquina) Permitir(de, evento, para string) *Maquina {
	if m.transicoes[de] == nil {
		m.transicoes[de] = map[string]string{}
	}
	m.transicoes[de][evento] = para
	return m
}

// AoMudar registra um callback chamado após cada transição.
func (m *Maquina) AoMudar(f func(de, evento, para string)) { m.aoMudar = f }

// Estado devolve o estado atual.
func (m *Maquina) Estado() string { return m.estado }

// Historico devolve a sequência de estados percorridos.
func (m *Maquina) Historico() []string { return append([]string(nil), m.historico...) }

// Pode informa se o evento é válido no estado atual.
func (m *Maquina) Pode(evento string) bool {
	_, ok := m.transicoes[m.estado][evento]
	return ok
}

// Disparar aplica o evento, mudando de estado se permitido.
func (m *Maquina) Disparar(evento string) error {
	para, ok := m.transicoes[m.estado][evento]
	if !ok {
		return fmt.Errorf("%w: evento %q no estado %q", ErrTransicaoInvalida, evento, m.estado)
	}
	de := m.estado
	m.estado = para
	m.historico = append(m.historico, para)
	if m.aoMudar != nil {
		m.aoMudar(de, evento, para)
	}
	return nil
}

// NovoPedido devolve uma máquina com o fluxo de um pedido de loja.
func NovoPedido() *Maquina {
	return Nova("criado").
		Permitir("criado", "pagar", "pago").
		Permitir("criado", "cancelar", "cancelado").
		Permitir("pago", "enviar", "enviado").
		Permitir("pago", "cancelar", "cancelado").
		Permitir("enviado", "entregar", "entregue")
}
