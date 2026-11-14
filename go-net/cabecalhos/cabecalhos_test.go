package cabecalhos

import (
	"bytes"
	"encoding/hex"
	"errors"
	"reflect"
	"testing"
)

var (
	ipA = [4]byte{192, 168, 0, 1}
	ipB = [4]byte{192, 168, 0, 199}
)

func TestIPv4VetorConhecido(t *testing.T) {
	// Cabeçalho clássico de exemplo: checksum 0xb861, TotalLen 0x73 (115).
	cab, _ := hex.DecodeString("45000073000040004011b861c0a80001c0a800c7")
	pacote := append(cab, make([]byte, 115-20)...)
	h, payload, err := ParseIPv4(pacote)
	if err != nil {
		t.Fatal(err)
	}
	if h.TotalLen != 115 || h.TTL != 64 || h.Proto != ProtoUDP || h.Flags != IPv4DF || h.FragOffset != 0 ||
		h.Checksum != 0xb861 || h.Origem != ipA || h.Destino != ipB || len(payload) != 95 {
		t.Errorf("campos inesperados: %+v", h)
	}
	// Serializar com os mesmos campos deve reproduzir os bytes exatos.
	saida, err := IPv4{TTL: 64, Proto: ProtoUDP, Flags: IPv4DF, Origem: ipA, Destino: ipB}.Serializar(make([]byte, 95))
	if err != nil {
		t.Fatal(err)
	}
	if !bytes.Equal(saida, pacote) {
		t.Errorf("serialização difere:\n%x\n%x", saida, pacote)
	}
}

func TestIPv4IdaEVolta(t *testing.T) {
	h := IPv4{TOS: 0x10, ID: 0xBEEF, Flags: IPv4MF, FragOffset: 185, TTL: 3, Proto: ProtoTCP,
		Origem: [4]byte{10, 0, 0, 1}, Destino: [4]byte{10, 0, 0, 2}, Opcoes: []byte{1, 1, 1, 0}}
	payload := []byte("olá, rede")
	b, err := h.Serializar(payload)
	if err != nil {
		t.Fatal(err)
	}
	if b[0] != 0x46 {
		t.Errorf("byte 0 = %#x, esperava 0x46 (IHL 6)", b[0])
	}
	got, pl, err := ParseIPv4(b)
	if err != nil {
		t.Fatal(err)
	}
	got.Checksum, got.TotalLen = 0, 0
	if !reflect.DeepEqual(got, h) || !bytes.Equal(pl, payload) {
		t.Errorf("ida e volta divergiu: %+v / %q", got, pl)
	}
}

func TestIPv4PayloadTruncadoPorTotalLen(t *testing.T) {
	b, _ := IPv4{TTL: 1, Origem: ipA, Destino: ipB}.Serializar([]byte{1, 2, 3})
	b = append(b, 0xAA, 0xBB) // lixo de preenchimento (ex.: padding Ethernet)
	_, pl, err := ParseIPv4(b)
	if err != nil || !bytes.Equal(pl, []byte{1, 2, 3}) {
		t.Errorf("payload = %v, err=%v", pl, err)
	}
}

func TestIPv4Malformado(t *testing.T) {
	bom, _ := IPv4{TTL: 9, Origem: ipA, Destino: ipB}.Serializar([]byte{1, 2, 3, 4})
	mut := func(f func(b []byte)) []byte {
		c := append([]byte(nil), bom...)
		f(c)
		return c
	}
	casos := []struct {
		nome string
		dado []byte
		erro error
	}{
		{"vazio", nil, ErrCurto},
		{"curto", bom[:19], ErrCurto},
		{"versao 6", mut(func(b []byte) { b[0] = 0x65 }), ErrVersao},
		{"ihl pequeno", mut(func(b []byte) { b[0] = 0x44 }), ErrTamanho},
		{"ihl maior que dados", mut(func(b []byte) { b[0] = 0x4F; b[2], b[3] = 0, 24 }), ErrCurto},
		{"totallen maior", mut(func(b []byte) { b[3] = 200 }), ErrTamanho},
		{"totallen menor que cabecalho", mut(func(b []byte) { b[2], b[3] = 0, 10 }), ErrTamanho},
		{"checksum", mut(func(b []byte) { b[8]++ }), ErrChecksum},
	}
	for _, c := range casos {
		if _, _, err := ParseIPv4(c.dado); !errors.Is(err, c.erro) {
			t.Errorf("%s: err=%v, esperava %v", c.nome, err, c.erro)
		}
	}
}

func TestIPv4SerializarInvalido(t *testing.T) {
	if _, err := (IPv4{Opcoes: []byte{1, 2, 3}}).Serializar(nil); !errors.Is(err, ErrOpcoes) {
		t.Errorf("opções não múltiplas de 4: %v", err)
	}
	if _, err := (IPv4{Opcoes: make([]byte, 44)}).Serializar(nil); !errors.Is(err, ErrOpcoes) {
		t.Errorf("opções > 40: %v", err)
	}
	if _, err := (IPv4{}).Serializar(make([]byte, 70000)); !errors.Is(err, ErrTamanho) {
		t.Errorf("pacote gigante: %v", err)
	}
	if _, err := (IPv4{Flags: 8}).Serializar(nil); !errors.Is(err, ErrTamanho) {
		t.Errorf("flags inválidas: %v", err)
	}
	if _, err := (IPv4{FragOffset: 0x2000}).Serializar(nil); !errors.Is(err, ErrTamanho) {
		t.Errorf("fragmento inválido: %v", err)
	}
}

func TestUDP(t *testing.T) {
	u := UDP{PortaOrigem: 5353, PortaDestino: 53}
	payload := []byte("consulta")
	b, err := u.Serializar(ipA, ipB, payload)
	if err != nil {
		t.Fatal(err)
	}
	if len(b) != 16 || b[4] != 0 || b[5] != 16 {
		t.Errorf("tamanho/campo length incorreto: %x", b)
	}
	got, pl, err := ParseUDP(b, ipA, ipB)
	if err != nil {
		t.Fatal(err)
	}
	if got.PortaOrigem != 5353 || got.PortaDestino != 53 || got.Tamanho != 16 || !bytes.Equal(pl, payload) {
		t.Errorf("ParseUDP = %+v %q", got, pl)
	}
	// Endereço errado no pseudo-cabeçalho invalida o checksum.
	if _, _, err := ParseUDP(b, ipA, [4]byte{1, 1, 1, 1}); !errors.Is(err, ErrChecksum) {
		t.Errorf("pseudo-cabeçalho errado: %v", err)
	}
	// Corrupção de payload.
	c := append([]byte(nil), b...)
	c[10] ^= 0xFF
	if _, _, err := ParseUDP(c, ipA, ipB); !errors.Is(err, ErrChecksum) {
		t.Errorf("payload corrompido: %v", err)
	}
	// Checksum zero = não calculado: aceito.
	c = append([]byte(nil), b...)
	c[6], c[7] = 0, 0
	c[10] ^= 0xFF
	if _, _, err := ParseUDP(c, ipA, ipB); err != nil {
		t.Errorf("checksum zero deveria ser aceito: %v", err)
	}
}

func TestUDPMalformado(t *testing.T) {
	b, _ := UDP{PortaOrigem: 1, PortaDestino: 2}.Serializar(ipA, ipB, []byte{9})
	if _, _, err := ParseUDP(b[:7], ipA, ipB); !errors.Is(err, ErrCurto) {
		t.Errorf("curto: %v", err)
	}
	c := append([]byte(nil), b...)
	c[5] = 200
	if _, _, err := ParseUDP(c, ipA, ipB); !errors.Is(err, ErrTamanho) {
		t.Errorf("length maior: %v", err)
	}
	c[4], c[5] = 0, 4
	if _, _, err := ParseUDP(c, ipA, ipB); !errors.Is(err, ErrTamanho) {
		t.Errorf("length < 8: %v", err)
	}
	if _, err := (UDP{}).Serializar(ipA, ipB, make([]byte, 70000)); !errors.Is(err, ErrTamanho) {
		t.Errorf("payload gigante: %v", err)
	}
}

func TestTCP(t *testing.T) {
	seg := TCP{PortaOrigem: 49152, PortaDestino: 80, Seq: 0xDEADBEEF, Ack: 0x01020304,
		Flags: TCPSyn | TCPAck, Janela: 65535, Urgente: 7,
		Opcoes: []byte{2, 4, 5, 0xb4}} // MSS 1460
	payload := []byte("GET / HTTP/1.1\r\n")
	b, err := seg.Serializar(ipA, ipB, payload)
	if err != nil {
		t.Fatal(err)
	}
	if b[12] != 6<<4 || b[13] != 0x12 {
		t.Errorf("offset/flags = %#x %#x", b[12], b[13])
	}
	got, pl, err := ParseTCP(b, ipA, ipB)
	if err != nil {
		t.Fatal(err)
	}
	got.Checksum = 0
	if !reflect.DeepEqual(got, seg) || !bytes.Equal(pl, payload) {
		t.Errorf("ida e volta divergiu: %+v %q", got, pl)
	}
	if _, _, err := ParseTCP(b, ipB, ipA); err != nil {
		// Trocar origem/destino não altera a soma (comutativa): deve passar.
		t.Errorf("troca de origem/destino mantém soma: %v", err)
	}
	if _, _, err := ParseTCP(b, ipA, [4]byte{9, 9, 9, 9}); !errors.Is(err, ErrChecksum) {
		t.Errorf("IP errado: %v", err)
	}
}

func TestTCPSemPayloadNemOpcoes(t *testing.T) {
	b, err := TCP{PortaOrigem: 1, PortaDestino: 2, Flags: TCPFin}.Serializar(ipA, ipB, nil)
	if err != nil || len(b) != 20 {
		t.Fatalf("len=%d err=%v", len(b), err)
	}
	got, pl, err := ParseTCP(b, ipA, ipB)
	if err != nil || len(pl) != 0 || got.Flags != TCPFin || got.Opcoes != nil {
		t.Errorf("%+v %v %v", got, pl, err)
	}
}

func TestTCPMalformado(t *testing.T) {
	b, _ := TCP{PortaOrigem: 1, PortaDestino: 2}.Serializar(ipA, ipB, []byte{1, 2})
	if _, _, err := ParseTCP(b[:19], ipA, ipB); !errors.Is(err, ErrCurto) {
		t.Errorf("curto: %v", err)
	}
	c := append([]byte(nil), b...)
	c[12] = 4 << 4 // offset < 5
	if _, _, err := ParseTCP(c, ipA, ipB); !errors.Is(err, ErrTamanho) {
		t.Errorf("offset pequeno: %v", err)
	}
	c[12] = 15 << 4 // offset além dos dados
	if _, _, err := ParseTCP(c, ipA, ipB); !errors.Is(err, ErrTamanho) {
		t.Errorf("offset grande: %v", err)
	}
	if _, err := (TCP{Opcoes: []byte{1}}).Serializar(ipA, ipB, nil); !errors.Is(err, ErrOpcoes) {
		t.Errorf("opções inválidas: %v", err)
	}
	if _, err := (TCP{}).Serializar(ipA, ipB, make([]byte, 70000)); !errors.Is(err, ErrTamanho) {
		t.Errorf("segmento gigante: %v", err)
	}
}

// Empilha IPv4 + UDP e desempilha, como um pacote real.
func TestPilhaIPv4UDP(t *testing.T) {
	udp, _ := UDP{PortaOrigem: 1000, PortaDestino: 2000}.Serializar(ipA, ipB, []byte("dados"))
	pacote, err := IPv4{TTL: 64, Proto: ProtoUDP, Origem: ipA, Destino: ipB}.Serializar(udp)
	if err != nil {
		t.Fatal(err)
	}
	ip, corpo, err := ParseIPv4(pacote)
	if err != nil || ip.Proto != ProtoUDP {
		t.Fatal(err)
	}
	_, dados, err := ParseUDP(corpo, ip.Origem, ip.Destino)
	if err != nil || string(dados) != "dados" {
		t.Errorf("dados=%q err=%v", dados, err)
	}
}
