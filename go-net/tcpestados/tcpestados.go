// Pacote tcpestados implementa a máquina de estados de conexão do TCP
// (RFC 9293, seção 3.3.2), com eventos de aplicação e de segmentos recebidos.
package tcpestados

import (
	"errors"
	"fmt"
)

// Estado é um estado da conexão TCP.
type Estado int

// Estados do diagrama TCP.
const (
	Closed Estado = iota
	Listen
	SynSent
	SynRcvd
	Established
	FinWait1
	FinWait2
	CloseWait
	Closing
	LastAck
	TimeWait
)

var nomesEstado = [...]string{"CLOSED", "LISTEN", "SYN-SENT", "SYN-RECEIVED", "ESTABLISHED",
	"FIN-WAIT-1", "FIN-WAIT-2", "CLOSE-WAIT", "CLOSING", "LAST-ACK", "TIME-WAIT"}

func (e Estado) String() string {
	if e < 0 || int(e) >= len(nomesEstado) {
		return fmt.Sprintf("Estado(%d)", int(e))
	}
	return nomesEstado[e]
}

// Evento é um estímulo à máquina: chamada da aplicação, segmento recebido ou timer.
type Evento int

// Eventos tratados.
const (
	AbrirPassivo Evento = iota // aplicação: listen
	AbrirAtivo                 // aplicação: connect
	Fechar                     // aplicação: close
	RecvSYN
	RecvSYNACK
	RecvACK
	RecvFIN
	RecvFINACK // FIN que também confirma nosso FIN
	RecvRST
	Timeout2MSL
)

var nomesEvento = [...]string{"AbrirPassivo", "AbrirAtivo", "Fechar", "RecvSYN", "RecvSYNACK",
	"RecvACK", "RecvFIN", "RecvFINACK", "RecvRST", "Timeout2MSL"}

func (e Evento) String() string {
	if e < 0 || int(e) >= len(nomesEvento) {
		return fmt.Sprintf("Evento(%d)", int(e))
	}
	return nomesEvento[e]
}

// ErrTransicao indica um evento que não é válido no estado atual.
var ErrTransicao = errors.New("tcpestados: transição inválida")

type transicao struct {
	proximo Estado
	acao    string // segmento a transmitir em resposta ("" = nenhum)
}

type chave struct {
	e  Estado
	ev Evento
}

var tabela = map[chave]transicao{
	{Closed, AbrirPassivo}: {Listen, ""},
	{Closed, AbrirAtivo}:   {SynSent, "SYN"},

	{Listen, RecvSYN}:    {SynRcvd, "SYN+ACK"},
	{Listen, AbrirAtivo}: {SynSent, "SYN"},
	{Listen, Fechar}:     {Closed, ""},

	{SynSent, RecvSYNACK}: {Established, "ACK"},
	{SynSent, RecvSYN}:    {SynRcvd, "SYN+ACK"}, // abertura simultânea
	{SynSent, Fechar}:     {Closed, ""},

	{SynRcvd, RecvACK}: {Established, ""},
	{SynRcvd, Fechar}:  {FinWait1, "FIN"},

	{Established, Fechar}:  {FinWait1, "FIN"},
	{Established, RecvFIN}: {CloseWait, "ACK"},

	{FinWait1, RecvACK}:    {FinWait2, ""},
	{FinWait1, RecvFIN}:    {Closing, "ACK"},
	{FinWait1, RecvFINACK}: {TimeWait, "ACK"},

	{FinWait2, RecvFIN}: {TimeWait, "ACK"},

	{CloseWait, Fechar}: {LastAck, "FIN"},

	{Closing, RecvACK}: {TimeWait, ""},

	{LastAck, RecvACK}: {Closed, ""},

	{TimeWait, Timeout2MSL}: {Closed, ""},
}

// Maquina é uma conexão TCP em termos de estado. Começa em Closed.
type Maquina struct {
	estado Estado
}

// Estado devolve o estado atual.
func (m *Maquina) Estado() Estado { return m.estado }

// Tratar aplica um evento. Devolve o segmento que deve ser enviado como
// resposta ("SYN", "SYN+ACK", "ACK", "FIN" ou "" se nada). Um RST recebido
// leva qualquer conexão sincronizada de volta a Closed. Eventos inválidos
// não alteram o estado e devolvem ErrTransicao.
func (m *Maquina) Tratar(ev Evento) (string, error) {
	if ev == RecvRST && m.estado != Closed && m.estado != Listen && m.estado != TimeWait {
		m.estado = Closed
		return "", nil
	}
	t, ok := tabela[chave{m.estado, ev}]
	if !ok {
		return "", fmt.Errorf("%w: %s em %s", ErrTransicao, ev, m.estado)
	}
	m.estado = t.proximo
	return t.acao, nil
}

// PodeEnviar informa se a aplicação pode enviar dados no estado atual.
func (m *Maquina) PodeEnviar() bool { return m.estado == Established || m.estado == CloseWait }

// PodeReceber informa se ainda é possível receber dados do par.
func (m *Maquina) PodeReceber() bool {
	return m.estado == Established || m.estado == FinWait1 || m.estado == FinWait2
}
