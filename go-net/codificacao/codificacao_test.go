package codificacao

import (
	"bytes"
	"encoding/base64"
	"errors"
	"math"
	"testing"
)

func TestBase64VetoresRFC4648(t *testing.T) {
	casos := []struct{ entrada, saida string }{
		{"", ""},
		{"f", "Zg=="},
		{"fo", "Zm8="},
		{"foo", "Zm9v"},
		{"foob", "Zm9vYg=="},
		{"fooba", "Zm9vYmE="},
		{"foobar", "Zm9vYmFy"},
		{"\xff\xff\xff", "////"},
		{"\xfb\xef\xbe", "++++"},
	}
	for _, c := range casos {
		if got := Base64([]byte(c.entrada)); got != c.saida {
			t.Errorf("Base64(%q) = %q, esperava %q", c.entrada, got, c.saida)
		}
		got, err := DecodificarBase64(c.saida)
		if err != nil || string(got) != c.entrada {
			t.Errorf("DecodificarBase64(%q) = %q, %v", c.saida, got, err)
		}
	}
}

func TestBase64ContraStdlib(t *testing.T) {
	for n := 0; n < 40; n++ {
		d := make([]byte, n)
		for i := range d {
			d[i] = byte(i*37 + n)
		}
		if got, want := Base64(d), base64.StdEncoding.EncodeToString(d); got != want {
			t.Errorf("n=%d: %q != %q", n, got, want)
		}
	}
}

func TestDecodificarBase64Invalido(t *testing.T) {
	casos := []struct {
		nome, s string
		erro    error
	}{
		{"tamanho", "Zm9", ErrTamanho},
		{"caractere", "Zm9!", ErrCaractere},
		{"espaço", "Zm 9", ErrCaractere},
		{"url-safe", "Zm9-", ErrCaractere},
		{"padding no meio", "Zg==Zm9v", ErrCaractere},
		{"padding demais", "Z===", ErrCaractere},
		{"bits residuais (1 pad)", "Zm9=", ErrCaractere},
		{"bits residuais (2 pad)", "Zh==", ErrCaractere},
		{"só padding", "====", ErrCaractere},
	}
	for _, c := range casos {
		if _, err := DecodificarBase64(c.s); !errors.Is(err, c.erro) {
			t.Errorf("%s (%q): err=%v, esperava %v", c.nome, c.s, err, c.erro)
		}
	}
}

func TestHex(t *testing.T) {
	casos := []struct {
		dados []byte
		hex   string
	}{
		{nil, ""},
		{[]byte{0x00}, "00"},
		{[]byte{0xDE, 0xAD, 0xBE, 0xEF}, "deadbeef"},
		{[]byte("Go"), "476f"},
	}
	for _, c := range casos {
		if got := Hex(c.dados); got != c.hex {
			t.Errorf("Hex = %q, esperava %q", got, c.hex)
		}
		got, err := DecodificarHex(c.hex)
		if err != nil || !bytes.Equal(got, c.dados) && len(got)+len(c.dados) > 0 {
			t.Errorf("DecodificarHex(%q) = %x, %v", c.hex, got, err)
		}
	}
	if got, _ := DecodificarHex("DeadBEEF"); !bytes.Equal(got, []byte{0xDE, 0xAD, 0xBE, 0xEF}) {
		t.Errorf("maiúsculas: %x", got)
	}
	if _, err := DecodificarHex("abc"); !errors.Is(err, ErrTamanho) {
		t.Errorf("tamanho ímpar: %v", err)
	}
	for _, s := range []string{"zz", "0g", "g0", "0x"} {
		if _, err := DecodificarHex(s); !errors.Is(err, ErrCaractere) {
			t.Errorf("%q: %v", s, err)
		}
	}
}

func TestVarintVetores(t *testing.T) {
	casos := []struct {
		v   uint64
		fio []byte
	}{
		{0, []byte{0x00}},
		{1, []byte{0x01}},
		{127, []byte{0x7F}},
		{128, []byte{0x80, 0x01}},
		{300, []byte{0xAC, 0x02}},
		{16384, []byte{0x80, 0x80, 0x01}},
		{math.MaxUint32, []byte{0xFF, 0xFF, 0xFF, 0xFF, 0x0F}},
		{math.MaxUint64, []byte{0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x01}},
	}
	for _, c := range casos {
		if got := AcrescentarVarint(nil, c.v); !bytes.Equal(got, c.fio) {
			t.Errorf("AcrescentarVarint(%d) = %x", c.v, got)
		}
		v, n, err := LerVarint(append(c.fio, 0xEE)) // byte extra não deve ser consumido
		if err != nil || v != c.v || n != len(c.fio) {
			t.Errorf("LerVarint(%x) = %d,%d,%v", c.fio, v, n, err)
		}
	}
}

func TestVarintInvalido(t *testing.T) {
	if _, _, err := LerVarint(nil); !errors.Is(err, ErrTruncado) {
		t.Errorf("vazio: %v", err)
	}
	if _, _, err := LerVarint([]byte{0x80, 0x80}); !errors.Is(err, ErrTruncado) {
		t.Errorf("truncado: %v", err)
	}
	onze := bytes.Repeat([]byte{0xFF}, 10)
	if _, _, err := LerVarint(append(onze, 0x01)); !errors.Is(err, ErrOverflow) {
		t.Errorf("11 bytes: %v", err)
	}
	// 10º byte maior que 1 estoura 64 bits.
	estouro := append(bytes.Repeat([]byte{0xFF}, 9), 0x02)
	if _, _, err := LerVarint(estouro); !errors.Is(err, ErrOverflow) {
		t.Errorf("10º byte 0x02: %v", err)
	}
}

func TestZigzag(t *testing.T) {
	casos := map[int64]uint64{0: 0, -1: 1, 1: 2, -2: 3, 2: 4, math.MaxInt64: math.MaxUint64 - 1, math.MinInt64: math.MaxUint64}
	for n, u := range casos {
		if got := Zigzag(n); got != u {
			t.Errorf("Zigzag(%d) = %d, esperava %d", n, got, u)
		}
		if got := DesZigzag(u); got != n {
			t.Errorf("DesZigzag(%d) = %d, esperava %d", u, got, n)
		}
	}
}

func TestVarintSinalIdaEVolta(t *testing.T) {
	for _, n := range []int64{0, 1, -1, 63, -64, 64, -65, 1 << 40, -(1 << 40), math.MaxInt64, math.MinInt64} {
		b := AcrescentarVarintSinal(nil, n)
		got, tam, err := LerVarintSinal(b)
		if err != nil || got != n || tam != len(b) {
			t.Errorf("%d: %d,%d,%v", n, got, tam, err)
		}
	}
	if b := AcrescentarVarintSinal(nil, -1); !bytes.Equal(b, []byte{0x01}) {
		t.Errorf("-1 deveria caber em 1 byte: %x", b)
	}
}
