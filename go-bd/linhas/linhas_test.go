package linhas

import (
	"bytes"
	"errors"
	"math"
	"math/rand"
	"reflect"
	"strings"
	"testing"
)

func esquemaPadrao(t *testing.T) Esquema {
	t.Helper()
	e, err := NovoEsquema(
		Coluna{"id", Inteiro, false},
		Coluna{"nome", Texto, false},
		Coluna{"saldo", Real, true},
		Coluna{"ativo", Booleano, false},
		Coluna{"foto", Bytes, true},
	)
	if err != nil {
		t.Fatal(err)
	}
	return e
}

func TestIdaEVolta(t *testing.T) {
	e := esquemaPadrao(t)
	casos := []struct {
		nome string
		in   []any
		quer []any
	}{
		{"tudo preenchido", []any{int64(42), "Ana", 12.5, true, []byte{1, 2, 3}}, []any{int64(42), "Ana", 12.5, true, []byte{1, 2, 3}}},
		{"nulos", []any{int64(1), "x", nil, false, nil}, []any{int64(1), "x", nil, false, nil}},
		{"int e float32 convertidos", []any{7, "y", float32(1.5), true, nil}, []any{int64(7), "y", 1.5, true, nil}},
		{"inteiro negativo e extremos", []any{int64(math.MinInt64), "", math.Inf(-1), false, []byte{}}, []any{int64(math.MinInt64), "", math.Inf(-1), false, []byte{}}},
		{"max int64", []any{int64(math.MaxInt64), "ç😀", -0.0, true, nil}, []any{int64(math.MaxInt64), "ç😀", -0.0, true, nil}},
		{"texto longo", []any{int64(0), strings.Repeat("ab", 5000), nil, true, nil}, []any{int64(0), strings.Repeat("ab", 5000), nil, true, nil}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			b, err := e.Codificar(c.in)
			if err != nil {
				t.Fatal(err)
			}
			got, err := e.Decodificar(b)
			if err != nil {
				t.Fatal(err)
			}
			if !reflect.DeepEqual(got, c.quer) {
				t.Fatalf("got %#v\nquer %#v", got, c.quer)
			}
		})
	}
}

func TestNaNPreservaBits(t *testing.T) {
	e, _ := NovoEsquema(Coluna{"f", Real, false})
	b, _ := e.Codificar([]any{math.NaN()})
	got, err := e.Decodificar(b)
	if err != nil || !math.IsNaN(got[0].(float64)) {
		t.Fatalf("got %v %v", got, err)
	}
}

func TestFormatoCompacto(t *testing.T) {
	e, _ := NovoEsquema(Coluna{"a", Inteiro, true}, Coluna{"b", Booleano, true})
	b, _ := e.Codificar([]any{nil, nil})
	if !bytes.Equal(b, []byte{0b11}) {
		t.Fatalf("bytes = %v", b)
	}
	b, _ = e.Codificar([]any{int64(-1), true})
	// bitmap 0, zigzag(-1) = 1, booleano 1
	if !bytes.Equal(b, []byte{0, 1, 1}) {
		t.Fatalf("bytes = %v", b)
	}
}

func TestMuitasColunasUsaVariosBytesDeBitmap(t *testing.T) {
	var cols []Coluna
	var vals []any
	for i := 0; i < 20; i++ {
		cols = append(cols, Coluna{Nome: string(rune('a' + i)), Tipo: Inteiro, Nulavel: true})
		if i%3 == 0 {
			vals = append(vals, nil)
		} else {
			vals = append(vals, int64(i))
		}
	}
	e, err := NovoEsquema(cols...)
	if err != nil {
		t.Fatal(err)
	}
	b, err := e.Codificar(vals)
	if err != nil {
		t.Fatal(err)
	}
	got, err := e.Decodificar(b)
	if err != nil || !reflect.DeepEqual(got, vals) {
		t.Fatalf("got %v err %v", got, err)
	}
}

func TestCodificarErros(t *testing.T) {
	e := esquemaPadrao(t)
	base := func() []any { return []any{int64(1), "n", 1.0, true, []byte{}} }
	casos := []struct {
		nome string
		muda func(v []any) []any
		quer error
	}{
		{"poucos valores", func(v []any) []any { return v[:3] }, ErrValor},
		{"valores demais", func(v []any) []any { return append(v, 1) }, ErrValor},
		{"nulo em não nulável", func(v []any) []any { v[0] = nil; return v }, ErrNulo},
		{"texto onde vai inteiro", func(v []any) []any { v[0] = "1"; return v }, ErrValor},
		{"inteiro onde vai texto", func(v []any) []any { v[1] = 5; return v }, ErrValor},
		{"inteiro onde vai real", func(v []any) []any { v[2] = 3; return v }, ErrValor},
		{"string onde vai bool", func(v []any) []any { v[3] = "true"; return v }, ErrValor},
		{"string onde vão bytes", func(v []any) []any { v[4] = "abc"; return v }, ErrValor},
		{"utf8 inválido", func(v []any) []any { v[1] = "a\xffb"; return v }, ErrValor},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if _, err := e.Codificar(c.muda(base())); !errors.Is(err, c.quer) {
				t.Fatalf("err = %v, quer %v", err, c.quer)
			}
		})
	}
}

func TestDecodificarCorrompida(t *testing.T) {
	e := esquemaPadrao(t)
	bom, _ := e.Codificar([]any{int64(300), "texto", 2.5, true, []byte("fotografia")})
	casos := []struct {
		nome string
		b    []byte
	}{
		{"vazia", nil},
		{"só bitmap", bom[:1]},
		{"bytes sobrando", append(append([]byte(nil), bom...), 9)},
		{"bit extra no bitmap", func() []byte { b := append([]byte(nil), bom...); b[0] |= 0b1000_0000; return b }()},
		{"nulo em não nulável", func() []byte { b := append([]byte(nil), bom...); b[0] |= 1; return b }()},
		{"booleano inválido", func() []byte {
			x, _ := e.Codificar([]any{int64(1), "", nil, true, nil})
			x[len(x)-1] = 7
			return x
		}()},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if _, err := e.Decodificar(c.b); !errors.Is(err, ErrCorrompida) {
				t.Fatalf("err = %v", err)
			}
		})
	}
	// qualquer prefixo próprio da linha válida deve ser rejeitado
	for n := 0; n < len(bom); n++ {
		if _, err := e.Decodificar(bom[:n]); !errors.Is(err, ErrCorrompida) {
			t.Fatalf("prefixo de %d bytes aceito (err = %v)", n, err)
		}
	}
}

func TestDecodificarTamanhoGiganteNaoAloca(t *testing.T) {
	e, _ := NovoEsquema(Coluna{"t", Texto, false})
	// bitmap 0, tamanho declarado de 2^60 bytes
	b := []byte{0, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x80, 0x10}
	if _, err := e.Decodificar(b); !errors.Is(err, ErrCorrompida) {
		t.Fatalf("err = %v", err)
	}
}

func TestDecodificarUTF8Invalido(t *testing.T) {
	e, _ := NovoEsquema(Coluna{"t", Texto, false})
	if _, err := e.Decodificar([]byte{0, 2, 0xff, 0xfe}); !errors.Is(err, ErrCorrompida) {
		t.Fatalf("err = %v", err)
	}
}

func TestBytesDecodificadosSaoCopia(t *testing.T) {
	e, _ := NovoEsquema(Coluna{"b", Bytes, false})
	buf, _ := e.Codificar([]any{[]byte{1, 2, 3}})
	got, _ := e.Decodificar(buf)
	buf[len(buf)-1] = 99
	if got[0].([]byte)[2] != 3 {
		t.Fatal("o resultado compartilha memória com o buffer de entrada")
	}
}

func TestEsquemaInvalido(t *testing.T) {
	casos := []struct {
		nome string
		cols []Coluna
	}{
		{"sem colunas", nil},
		{"nome vazio", []Coluna{{"", Inteiro, false}}},
		{"nome repetido", []Coluna{{"a", Inteiro, false}, {"a", Texto, false}}},
		{"tipo inválido", []Coluna{{"a", Tipo(0), false}}},
		{"tipo desconhecido", []Coluna{{"a", Tipo(99), false}}},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if _, err := NovoEsquema(c.cols...); !errors.Is(err, ErrEsquema) {
				t.Fatalf("err = %v", err)
			}
		})
	}
}

func TestIndiceETipo(t *testing.T) {
	e := esquemaPadrao(t)
	if e.Indice("saldo") != 2 || e.Indice("zzz") != -1 {
		t.Fatal("Indice")
	}
	if Texto.String() != "TEXTO" || Tipo(77).String() != "TIPO(77)" {
		t.Fatal("String")
	}
	var t2 Tipo
	if err := t2.UnmarshalText([]byte("REAL")); err != nil || t2 != Real {
		t.Fatalf("UnmarshalText: %v", err)
	}
	if err := t2.UnmarshalText([]byte("nada")); !errors.Is(err, ErrTipoInvalido) {
		t.Fatalf("UnmarshalText inválido: %v", err)
	}
	if _, err := Tipo(50).MarshalText(); !errors.Is(err, ErrTipoInvalido) {
		t.Fatalf("MarshalText inválido: %v", err)
	}
}

func TestAleatorio(t *testing.T) {
	e := esquemaPadrao(t)
	r := rand.New(rand.NewSource(13))
	for i := 0; i < 500; i++ {
		foto := make([]byte, r.Intn(40))
		r.Read(foto)
		nome := make([]rune, r.Intn(20))
		for j := range nome {
			nome[j] = rune('a' + r.Intn(26))
		}
		var saldo any
		if r.Intn(2) == 0 {
			saldo = r.NormFloat64()
		}
		in := []any{r.Int63() - r.Int63(), string(nome), saldo, r.Intn(2) == 0, foto}
		b, err := e.Codificar(in)
		if err != nil {
			t.Fatal(err)
		}
		got, err := e.Decodificar(b)
		if err != nil {
			t.Fatal(err)
		}
		in[4] = append([]byte{}, foto...)
		if !reflect.DeepEqual(got, in) {
			t.Fatalf("linha %d diverge:\n%#v\n%#v", i, got, in)
		}
	}
}
