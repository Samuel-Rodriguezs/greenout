package checksum

import (
	"encoding/binary"
	"testing"
)

func TestVetoresConhecidos(t *testing.T) {
	casos := []struct {
		nome  string
		dados []byte
		soma  uint16
		cks   uint16
	}{
		{"vazio", nil, 0x0000, 0xFFFF},
		{"RFC 1071", []byte{0x00, 0x01, 0xf2, 0x03, 0xf4, 0xf5, 0xf6, 0xf7}, 0xddf2, 0x220d},
		{"impar", []byte{0x01, 0x02, 0x03}, 0x0402, 0xfbfd},
		{"um byte", []byte{0xFF}, 0xFF00, 0x00FF},
		{"carry", []byte{0xFF, 0xFF, 0x00, 0x01}, 0x0001, 0xFFFE},
		// Cabeçalho IPv4 clássico com o campo de checksum (bytes 10-11) zerado.
		{"ipv4", []byte{0x45, 0x00, 0x00, 0x73, 0x00, 0x00, 0x40, 0x00, 0x40, 0x11, 0x00, 0x00,
			0xc0, 0xa8, 0x00, 0x01, 0xc0, 0xa8, 0x00, 0xc7}, 0x479e, 0xb861},
	}
	for _, c := range casos {
		if got := Soma(c.dados); got != c.soma {
			t.Errorf("%s: Soma = %#04x, esperava %#04x", c.nome, got, c.soma)
		}
		if got := Calcular(c.dados); got != c.cks {
			t.Errorf("%s: Calcular = %#04x, esperava %#04x", c.nome, got, c.cks)
		}
	}
}

func TestVerifica(t *testing.T) {
	cab := []byte{0x45, 0x00, 0x00, 0x73, 0x00, 0x00, 0x40, 0x00, 0x40, 0x11, 0xb8, 0x61,
		0xc0, 0xa8, 0x00, 0x01, 0xc0, 0xa8, 0x00, 0xc7}
	if !Verifica(cab) {
		t.Error("cabeçalho válido rejeitado")
	}
	cab[3] ^= 0x01
	if Verifica(cab) {
		t.Error("cabeçalho corrompido aceito")
	}
	// Anexar o checksum aos dados deve sempre verificar (inclusive tamanho par).
	dados := []byte{0xde, 0xad, 0xbe, 0xef, 0x12, 0x34}
	cks := Calcular(dados)
	com := binary.BigEndian.AppendUint16(append([]byte(nil), dados...), cks)
	if !Verifica(com) {
		t.Error("dados + checksum deveriam verificar")
	}
}

func TestCalcularVarios(t *testing.T) {
	a := []byte{0x12, 0x34, 0x56, 0x78}
	b := []byte{0x9a, 0xbc, 0xde}
	junto := append(append([]byte(nil), a...), b...)
	if CalcularVarios(a, b) != Calcular(junto) {
		t.Error("CalcularVarios difere da concatenação")
	}
	if CalcularVarios() != 0xFFFF {
		t.Error("sem blocos deveria dar 0xFFFF")
	}
}

func TestAtualizarIncremental(t *testing.T) {
	dados := []byte{0x45, 0x00, 0x00, 0x73, 0x00, 0x00, 0x40, 0x00, 0x40, 0x11, 0x00, 0x00,
		0xc0, 0xa8, 0x00, 0x01, 0xc0, 0xa8, 0x00, 0xc7}
	original := Calcular(dados)
	// Decrementa o TTL (byte 8) como faria um roteador: palavra 0x4011 -> 0x3f11.
	antigo := binary.BigEndian.Uint16(dados[8:])
	dados[8]--
	novo := binary.BigEndian.Uint16(dados[8:])
	if got, want := Atualizar(original, antigo, novo), Calcular(dados); got != want {
		t.Errorf("Atualizar = %#04x, recálculo = %#04x", got, want)
	}
	// Varre várias mudanças de palavra e compara com o recálculo completo.
	for _, nv := range []uint16{0x0000, 0xFFFF, 0x1234, 0x8000} {
		d := append([]byte(nil), dados...)
		ck := Calcular(d)
		ant := binary.BigEndian.Uint16(d[12:])
		binary.BigEndian.PutUint16(d[12:], nv)
		if Atualizar(ck, ant, nv) != Calcular(d) {
			t.Errorf("Atualizar divergiu para novo=%#04x", nv)
		}
	}
}
