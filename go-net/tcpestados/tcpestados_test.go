package tcpestados

import (
	"errors"
	"testing"
)

func TestTransicoesValidas(t *testing.T) {
	casos := []struct {
		de   Estado
		ev   Evento
		para Estado
		acao string
	}{
		{Closed, AbrirPassivo, Listen, ""},
		{Closed, AbrirAtivo, SynSent, "SYN"},
		{Listen, RecvSYN, SynRcvd, "SYN+ACK"},
		{Listen, AbrirAtivo, SynSent, "SYN"},
		{Listen, Fechar, Closed, ""},
		{SynSent, RecvSYNACK, Established, "ACK"},
		{SynSent, RecvSYN, SynRcvd, "SYN+ACK"},
		{SynSent, Fechar, Closed, ""},
		{SynRcvd, RecvACK, Established, ""},
		{SynRcvd, Fechar, FinWait1, "FIN"},
		{Established, Fechar, FinWait1, "FIN"},
		{Established, RecvFIN, CloseWait, "ACK"},
		{FinWait1, RecvACK, FinWait2, ""},
		{FinWait1, RecvFIN, Closing, "ACK"},
		{FinWait1, RecvFINACK, TimeWait, "ACK"},
		{FinWait2, RecvFIN, TimeWait, "ACK"},
		{CloseWait, Fechar, LastAck, "FIN"},
		{Closing, RecvACK, TimeWait, ""},
		{LastAck, RecvACK, Closed, ""},
		{TimeWait, Timeout2MSL, Closed, ""},
	}
	for _, c := range casos {
		m := &Maquina{estado: c.de}
		acao, err := m.Tratar(c.ev)
		if err != nil || m.Estado() != c.para || acao != c.acao {
			t.Errorf("%s + %s -> %s %q err=%v; esperava %s %q", c.de, c.ev, m.Estado(), acao, err, c.para, c.acao)
		}
	}
}

func TestTransicoesInvalidasNaoMudamEstado(t *testing.T) {
	casos := []struct {
		de Estado
		ev Evento
	}{
		{Closed, RecvACK},
		{Closed, Fechar},
		{Listen, RecvACK},
		{SynSent, RecvFIN},
		{Established, RecvSYN},
		{Established, AbrirAtivo},
		{FinWait2, RecvACK},
		{CloseWait, RecvFIN},
		{LastAck, Fechar},
		{TimeWait, RecvACK},
		{Closed, Timeout2MSL},
		{Established, Timeout2MSL},
	}
	for _, c := range casos {
		m := &Maquina{estado: c.de}
		acao, err := m.Tratar(c.ev)
		if !errors.Is(err, ErrTransicao) || m.Estado() != c.de || acao != "" {
			t.Errorf("%s + %s deveria ser inválido (estado=%s err=%v)", c.de, c.ev, m.Estado(), err)
		}
	}
}

func TestRSTFechaConexaoSincronizada(t *testing.T) {
	for _, e := range []Estado{SynSent, SynRcvd, Established, FinWait1, FinWait2, CloseWait, Closing, LastAck} {
		m := &Maquina{estado: e}
		if _, err := m.Tratar(RecvRST); err != nil || m.Estado() != Closed {
			t.Errorf("RST em %s -> %s err=%v", e, m.Estado(), err)
		}
	}
	// Em Listen o RST é ignorado como evento inválido; em Closed também.
	for _, e := range []Estado{Closed, Listen, TimeWait} {
		m := &Maquina{estado: e}
		if _, err := m.Tratar(RecvRST); !errors.Is(err, ErrTransicao) || m.Estado() != e {
			t.Errorf("RST em %s deveria ser inválido", e)
		}
	}
}

// executa uma sequência de eventos e confere os estados intermediários.
func executa(t *testing.T, nome string, evs []Evento, estados []Estado) {
	t.Helper()
	m := &Maquina{}
	for i, ev := range evs {
		if _, err := m.Tratar(ev); err != nil {
			t.Fatalf("%s passo %d (%s): %v", nome, i, ev, err)
		}
		if m.Estado() != estados[i] {
			t.Fatalf("%s passo %d: estado %s, esperava %s", nome, i, m.Estado(), estados[i])
		}
	}
}

func TestCenarios(t *testing.T) {
	executa(t, "cliente fecha primeiro",
		[]Evento{AbrirAtivo, RecvSYNACK, Fechar, RecvACK, RecvFIN, Timeout2MSL},
		[]Estado{SynSent, Established, FinWait1, FinWait2, TimeWait, Closed})
	executa(t, "servidor passivo, cliente fecha",
		[]Evento{AbrirPassivo, RecvSYN, RecvACK, RecvFIN, Fechar, RecvACK},
		[]Estado{Listen, SynRcvd, Established, CloseWait, LastAck, Closed})
	executa(t, "fechamento simultâneo",
		[]Evento{AbrirAtivo, RecvSYNACK, Fechar, RecvFIN, RecvACK, Timeout2MSL},
		[]Estado{SynSent, Established, FinWait1, Closing, TimeWait, Closed})
	executa(t, "FIN+ACK combinado",
		[]Evento{AbrirAtivo, RecvSYNACK, Fechar, RecvFINACK, Timeout2MSL},
		[]Estado{SynSent, Established, FinWait1, TimeWait, Closed})
	executa(t, "abertura simultânea",
		[]Evento{AbrirAtivo, RecvSYN, RecvACK},
		[]Estado{SynSent, SynRcvd, Established})
}

func TestPodeEnviarReceber(t *testing.T) {
	casos := map[Estado][2]bool{
		Closed: {false, false}, Listen: {false, false}, Established: {true, true},
		FinWait1: {false, true}, FinWait2: {false, true}, CloseWait: {true, false},
		LastAck: {false, false}, TimeWait: {false, false},
	}
	for e, want := range casos {
		m := &Maquina{estado: e}
		if m.PodeEnviar() != want[0] || m.PodeReceber() != want[1] {
			t.Errorf("%s: enviar/receber = %v/%v", e, m.PodeEnviar(), m.PodeReceber())
		}
	}
}

func TestStrings(t *testing.T) {
	if Established.String() != "ESTABLISHED" || TimeWait.String() != "TIME-WAIT" || Estado(99).String() != "Estado(99)" {
		t.Error("String de Estado")
	}
	if RecvSYNACK.String() != "RecvSYNACK" || Evento(-1).String() != "Evento(-1)" {
		t.Error("String de Evento")
	}
}
