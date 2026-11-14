// Pacote cabecalhos serializa e interpreta cabeçalhos IPv4, UDP e TCP com
// encoding/binary, incluindo o checksum com pseudo-cabeçalho.
package cabecalhos

import (
	"encoding/binary"
	"errors"
	"fmt"

	"greenout/net/checksum"
)

// Números de protocolo da camada de transporte.
const (
	ProtoTCP = 6
	ProtoUDP = 17
)

// Flags do campo de fragmentação do IPv4 (3 bits altos de Flags).
const (
	IPv4DF = 0x2 // don't fragment
	IPv4MF = 0x1 // more fragments
)

// Flags TCP.
const (
	TCPFin = 1 << iota
	TCPSyn
	TCPRst
	TCPPsh
	TCPAck
	TCPUrg
	TCPEce
	TCPCwr
)

// Erros de interpretação.
var (
	ErrCurto    = errors.New("cabecalhos: dados curtos demais")
	ErrVersao   = errors.New("cabecalhos: versão IP inválida")
	ErrTamanho  = errors.New("cabecalhos: campo de tamanho inválido")
	ErrChecksum = errors.New("cabecalhos: checksum inválido")
	ErrOpcoes   = errors.New("cabecalhos: opções com tamanho inválido")
)

// IPv4 representa o cabeçalho IPv4 (RFC 791).
type IPv4 struct {
	TOS        uint8
	TotalLen   uint16 // preenchido por Serializar a partir do payload
	ID         uint16
	Flags      uint8  // 3 bits
	FragOffset uint16 // 13 bits, em unidades de 8 bytes
	TTL        uint8
	Proto      uint8
	Checksum   uint16 // calculado em Serializar; lido em ParseIPv4
	Origem     [4]byte
	Destino    [4]byte
	Opcoes     []byte // tamanho múltiplo de 4, no máximo 40
}

// Serializar gera o cabeçalho (com checksum válido) seguido do payload.
// TotalLen é calculado automaticamente.
func (h IPv4) Serializar(payload []byte) ([]byte, error) {
	if len(h.Opcoes)%4 != 0 || len(h.Opcoes) > 40 {
		return nil, ErrOpcoes
	}
	tam := 20 + len(h.Opcoes)
	total := tam + len(payload)
	if total > 0xFFFF {
		return nil, fmt.Errorf("%w: pacote de %d bytes", ErrTamanho, total)
	}
	if h.Flags > 7 || h.FragOffset > 0x1FFF {
		return nil, fmt.Errorf("%w: flags/fragmento fora do intervalo", ErrTamanho)
	}
	b := make([]byte, total)
	b[0] = 4<<4 | byte(tam/4)
	b[1] = h.TOS
	binary.BigEndian.PutUint16(b[2:], uint16(total))
	binary.BigEndian.PutUint16(b[4:], h.ID)
	binary.BigEndian.PutUint16(b[6:], uint16(h.Flags)<<13|h.FragOffset)
	b[8] = h.TTL
	b[9] = h.Proto
	copy(b[12:16], h.Origem[:])
	copy(b[16:20], h.Destino[:])
	copy(b[20:], h.Opcoes)
	binary.BigEndian.PutUint16(b[10:], checksum.Calcular(b[:tam]))
	copy(b[tam:], payload)
	return b, nil
}

// ParseIPv4 interpreta um pacote, valida versão, tamanhos e checksum e
// devolve o cabeçalho e o payload (limitado por TotalLen).
func ParseIPv4(b []byte) (IPv4, []byte, error) {
	var h IPv4
	if len(b) < 20 {
		return h, nil, ErrCurto
	}
	if b[0]>>4 != 4 {
		return h, nil, ErrVersao
	}
	tam := int(b[0]&0xF) * 4
	if tam < 20 {
		return h, nil, fmt.Errorf("%w: IHL=%d", ErrTamanho, b[0]&0xF)
	}
	if len(b) < tam {
		return h, nil, ErrCurto
	}
	total := int(binary.BigEndian.Uint16(b[2:]))
	if total < tam || total > len(b) {
		return h, nil, fmt.Errorf("%w: TotalLen=%d", ErrTamanho, total)
	}
	if !checksum.Verifica(b[:tam]) {
		return h, nil, ErrChecksum
	}
	h.TOS = b[1]
	h.TotalLen = uint16(total)
	h.ID = binary.BigEndian.Uint16(b[4:])
	ff := binary.BigEndian.Uint16(b[6:])
	h.Flags = uint8(ff >> 13)
	h.FragOffset = ff & 0x1FFF
	h.TTL = b[8]
	h.Proto = b[9]
	h.Checksum = binary.BigEndian.Uint16(b[10:])
	copy(h.Origem[:], b[12:16])
	copy(h.Destino[:], b[16:20])
	if tam > 20 {
		h.Opcoes = append([]byte(nil), b[20:tam]...)
	}
	return h, b[tam:total], nil
}

// pseudoCabecalho monta o pseudo-cabeçalho IPv4 usado no checksum de UDP/TCP.
func pseudoCabecalho(orig, dest [4]byte, proto uint8, tamSeg int) []byte {
	p := make([]byte, 12)
	copy(p[0:4], orig[:])
	copy(p[4:8], dest[:])
	p[9] = proto
	binary.BigEndian.PutUint16(p[10:], uint16(tamSeg))
	return p
}

// ChecksumTransporte calcula o checksum de um segmento UDP/TCP (com o campo
// de checksum zerado) incluindo o pseudo-cabeçalho IPv4.
func ChecksumTransporte(orig, dest [4]byte, proto uint8, segmento []byte) uint16 {
	return checksum.CalcularVarios(pseudoCabecalho(orig, dest, proto, len(segmento)), segmento)
}

func verificaTransporte(orig, dest [4]byte, proto uint8, segmento []byte) bool {
	return checksum.Soma(append(pseudoCabecalho(orig, dest, proto, len(segmento)), segmento...)) == 0xFFFF
}

// UDP representa o cabeçalho UDP (RFC 768).
type UDP struct {
	PortaOrigem  uint16
	PortaDestino uint16
	Tamanho      uint16 // calculado em Serializar
	Checksum     uint16
}

// Serializar gera o datagrama UDP com checksum calculado sobre o
// pseudo-cabeçalho. Um checksum igual a zero é transmitido como 0xFFFF.
func (u UDP) Serializar(orig, dest [4]byte, payload []byte) ([]byte, error) {
	total := 8 + len(payload)
	if total > 0xFFFF {
		return nil, fmt.Errorf("%w: datagrama de %d bytes", ErrTamanho, total)
	}
	b := make([]byte, total)
	binary.BigEndian.PutUint16(b[0:], u.PortaOrigem)
	binary.BigEndian.PutUint16(b[2:], u.PortaDestino)
	binary.BigEndian.PutUint16(b[4:], uint16(total))
	copy(b[8:], payload)
	c := ChecksumTransporte(orig, dest, ProtoUDP, b)
	if c == 0 {
		c = 0xFFFF
	}
	binary.BigEndian.PutUint16(b[6:], c)
	return b, nil
}

// ParseUDP interpreta um datagrama UDP. Checksum zero significa "não
// calculado" (permitido em IPv4) e não é verificado.
func ParseUDP(b []byte, orig, dest [4]byte) (UDP, []byte, error) {
	var u UDP
	if len(b) < 8 {
		return u, nil, ErrCurto
	}
	tam := int(binary.BigEndian.Uint16(b[4:]))
	if tam < 8 || tam > len(b) {
		return u, nil, fmt.Errorf("%w: Tamanho=%d", ErrTamanho, tam)
	}
	u.PortaOrigem = binary.BigEndian.Uint16(b[0:])
	u.PortaDestino = binary.BigEndian.Uint16(b[2:])
	u.Tamanho = uint16(tam)
	u.Checksum = binary.BigEndian.Uint16(b[6:])
	if u.Checksum != 0 && !verificaTransporte(orig, dest, ProtoUDP, b[:tam]) {
		return u, nil, ErrChecksum
	}
	return u, b[8:tam], nil
}

// TCP representa o cabeçalho TCP (RFC 9293).
type TCP struct {
	PortaOrigem  uint16
	PortaDestino uint16
	Seq          uint32
	Ack          uint32
	Flags        uint8
	Janela       uint16
	Checksum     uint16
	Urgente      uint16
	Opcoes       []byte // tamanho múltiplo de 4, no máximo 40
}

// Serializar gera o segmento TCP (cabeçalho, opções e payload) com checksum.
func (t TCP) Serializar(orig, dest [4]byte, payload []byte) ([]byte, error) {
	if len(t.Opcoes)%4 != 0 || len(t.Opcoes) > 40 {
		return nil, ErrOpcoes
	}
	tam := 20 + len(t.Opcoes)
	b := make([]byte, tam+len(payload))
	if len(b) > 0xFFFF {
		return nil, fmt.Errorf("%w: segmento de %d bytes", ErrTamanho, len(b))
	}
	binary.BigEndian.PutUint16(b[0:], t.PortaOrigem)
	binary.BigEndian.PutUint16(b[2:], t.PortaDestino)
	binary.BigEndian.PutUint32(b[4:], t.Seq)
	binary.BigEndian.PutUint32(b[8:], t.Ack)
	b[12] = byte(tam/4) << 4
	b[13] = t.Flags
	binary.BigEndian.PutUint16(b[14:], t.Janela)
	binary.BigEndian.PutUint16(b[18:], t.Urgente)
	copy(b[20:], t.Opcoes)
	copy(b[tam:], payload)
	binary.BigEndian.PutUint16(b[16:], ChecksumTransporte(orig, dest, ProtoTCP, b))
	return b, nil
}

// ParseTCP interpreta um segmento TCP, validando offset e checksum.
func ParseTCP(b []byte, orig, dest [4]byte) (TCP, []byte, error) {
	var t TCP
	if len(b) < 20 {
		return t, nil, ErrCurto
	}
	tam := int(b[12]>>4) * 4
	if tam < 20 || tam > len(b) {
		return t, nil, fmt.Errorf("%w: data offset=%d", ErrTamanho, b[12]>>4)
	}
	if !verificaTransporte(orig, dest, ProtoTCP, b) {
		return t, nil, ErrChecksum
	}
	t.PortaOrigem = binary.BigEndian.Uint16(b[0:])
	t.PortaDestino = binary.BigEndian.Uint16(b[2:])
	t.Seq = binary.BigEndian.Uint32(b[4:])
	t.Ack = binary.BigEndian.Uint32(b[8:])
	t.Flags = b[13]
	t.Janela = binary.BigEndian.Uint16(b[14:])
	t.Checksum = binary.BigEndian.Uint16(b[16:])
	t.Urgente = binary.BigEndian.Uint16(b[18:])
	if tam > 20 {
		t.Opcoes = append([]byte(nil), b[20:tam]...)
	}
	return t, b[tam:], nil
}
