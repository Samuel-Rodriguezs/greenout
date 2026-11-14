package crcserial

import (
	"bytes"
	"errors"
	"hash/crc32"
	"io"
	"reflect"
	"testing"
)

func TestCRC32Vetores(t *testing.T) {
	casos := []struct {
		entrada string
		want    uint32
	}{
		{"", 0x00000000},
		{"a", 0xE8B7BE43},
		{"abc", 0x352441C2},
		{"123456789", 0xCBF43926}, // vetor de verificação padrão do CRC-32
		{"The quick brown fox jumps over the lazy dog", 0x414FA339},
	}
	for _, c := range casos {
		if got := CRC32([]byte(c.entrada)); got != c.want {
			t.Errorf("CRC32(%q) = %#08x, esperava %#08x", c.entrada, got, c.want)
		}
	}
}

func TestCRC32ContraStdlibEIncremental(t *testing.T) {
	dados := make([]byte, 1000)
	for i := range dados {
		dados[i] = byte(i * 7)
	}
	if CRC32(dados) != crc32.ChecksumIEEE(dados) {
		t.Error("diverge da stdlib")
	}
	for _, corte := range []int{0, 1, 500, 999, 1000} {
		if got := Atualizar(CRC32(dados[:corte]), dados[corte:]); got != CRC32(dados) {
			t.Errorf("incremental no corte %d: %#x", corte, got)
		}
	}
}

func TestSelarEAbrir(t *testing.T) {
	for _, corpo := range [][]byte{nil, []byte("x"), []byte("mensagem de teste"), bytes.Repeat([]byte{0xAB}, 5000)} {
		env, err := Selar(corpo)
		if err != nil {
			t.Fatal(err)
		}
		if len(env) != 7+len(corpo)+4 || env[0] != 'G' || env[1] != 'N' || env[2] != 1 {
			t.Errorf("envelope malformado: % x", env[:7])
		}
		got, err := Abrir(env)
		if err != nil || !bytes.Equal(got, corpo) {
			t.Errorf("Abrir: %v", err)
		}
		// Bytes sobrando depois do envelope são ignorados.
		if _, err := Abrir(append(append([]byte(nil), env...), 1, 2, 3)); err != nil {
			t.Errorf("com sobra: %v", err)
		}
	}
}

func TestCorrupcaoDetectadaEmQualquerByte(t *testing.T) {
	env, _ := Selar([]byte("dados importantes"))
	for i := range env {
		c := append([]byte(nil), env...)
		c[i] ^= 0x01
		if _, err := Abrir(c); err == nil {
			t.Errorf("flip no byte %d passou despercebido", i)
		}
	}
}

func TestAbrirMalformado(t *testing.T) {
	bom, _ := Selar([]byte("abc"))
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
		{"cabeçalho curto", bom[:6], ErrCurto},
		{"sem crc", bom[:len(bom)-1], ErrCurto},
		{"magic", mut(func(b []byte) { b[0] = 'X' }), ErrMagic},
		{"versão", mut(func(b []byte) { b[2] = 9 }), ErrVersao},
		{"tamanho gigante", mut(func(b []byte) { b[3] = 0xFF }), ErrGrande},
		{"tamanho maior que dados", mut(func(b []byte) { b[6] = 200 }), ErrCurto},
		{"crc", mut(func(b []byte) { b[len(b)-1]++ }), ErrCRC},
	}
	for _, c := range casos {
		if _, err := Abrir(c.dado); !errors.Is(err, c.erro) {
			t.Errorf("%s: err=%v, esperava %v", c.nome, err, c.erro)
		}
	}
	if _, err := Selar(make([]byte, MaxCorpo+1)); !errors.Is(err, ErrGrande) {
		t.Errorf("corpo gigante: %v", err)
	}
}

func TestFluxo(t *testing.T) {
	var buf bytes.Buffer
	corpos := [][]byte{[]byte("um"), {}, []byte("três")}
	for _, c := range corpos {
		if err := Escrever(&buf, c); err != nil {
			t.Fatal(err)
		}
	}
	for i, c := range corpos {
		got, err := Ler(&buf)
		if err != nil || !bytes.Equal(got, c) {
			t.Fatalf("envelope %d: %q %v", i, got, err)
		}
	}
	if _, err := Ler(&buf); err != io.EOF {
		t.Errorf("fim limpo deveria ser io.EOF: %v", err)
	}
}

func TestLerMalformado(t *testing.T) {
	bom, _ := Selar([]byte("abcdef"))
	casos := []struct {
		nome string
		dado []byte
		erro error
	}{
		{"cabeçalho parcial", bom[:3], io.ErrUnexpectedEOF},
		{"sem corpo", bom[:7], io.ErrUnexpectedEOF},
		{"corpo parcial", bom[:10], io.ErrUnexpectedEOF},
		{"magic", append([]byte("XX"), bom[2:]...), ErrMagic},
		{"crc", append(append([]byte(nil), bom[:len(bom)-1]...), bom[len(bom)-1]^1), ErrCRC},
	}
	for _, c := range casos {
		if _, err := Ler(bytes.NewReader(c.dado)); !errors.Is(err, c.erro) {
			t.Errorf("%s: err=%v, esperava %v", c.nome, err, c.erro)
		}
	}
}

func TestRegistro(t *testing.T) {
	casos := []Registro{
		{ID: 1, Nome: "sensor-a", Valores: []int32{1, -2, 3, 2147483647, -2147483648}},
		{ID: 0xFFFFFFFF, Nome: "", Valores: nil},
		{ID: 7, Nome: "acentuação ç ã", Valores: []int32{0}},
	}
	for _, r := range casos {
		env, err := SelarRegistro(r)
		if err != nil {
			t.Fatal(err)
		}
		got, err := AbrirRegistro(env)
		if err != nil || !reflect.DeepEqual(got, r) {
			t.Errorf("ida e volta de %+v: %+v %v", r, got, err)
		}
	}
}

func TestRegistroMalformado(t *testing.T) {
	bom, _ := Registro{ID: 1, Nome: "ab", Valores: []int32{5, 6}}.Marshal()
	for n := 0; n < len(bom); n++ {
		if _, err := UnmarshalRegistro(bom[:n]); err == nil {
			t.Errorf("prefixo de %d bytes deveria falhar", n)
		}
	}
	if _, err := UnmarshalRegistro(append(append([]byte(nil), bom...), 0)); err == nil {
		t.Error("byte sobrando deveria falhar")
	}
	if _, err := (Registro{Nome: string(make([]byte, 70000))}).Marshal(); !errors.Is(err, ErrGrande) {
		t.Errorf("nome gigante: %v", err)
	}
	if _, err := (Registro{Valores: make([]int32, 70000)}).Marshal(); !errors.Is(err, ErrGrande) {
		t.Errorf("valores demais: %v", err)
	}
	env, _ := SelarRegistro(Registro{ID: 1})
	env[8] ^= 0xFF
	if _, err := AbrirRegistro(env); !errors.Is(err, ErrCRC) {
		t.Errorf("corpo adulterado: %v", err)
	}
}
