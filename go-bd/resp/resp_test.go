package resp

import (
	"bufio"
	"bytes"
	"errors"
	"io"
	"reflect"
	"strings"
	"testing"
)

func TestCodificar(t *testing.T) {
	casos := []struct {
		nome string
		v    Valor
		quer string
	}{
		{"simples", NovoSimples("OK"), "+OK\r\n"},
		{"erro", NovoErro("ERR falhou"), "-ERR falhou\r\n"},
		{"inteiro", NovoInteiro(1000), ":1000\r\n"},
		{"inteiro negativo", NovoInteiro(-42), ":-42\r\n"},
		{"bulk", NovoBulk("foobar"), "$6\r\nfoobar\r\n"},
		{"bulk vazio", NovoBulk(""), "$0\r\n\r\n"},
		{"bulk com crlf", NovoBulk("a\r\nb"), "$4\r\na\r\nb\r\n"},
		{"bulk nulo", BulkNulo(), "$-1\r\n"},
		{"array vazio", NovoArray(), "*0\r\n"},
		{"array nulo", ArrayNulo(), "*-1\r\n"},
		{"comando", ComandoEmArray("SET", "k", "v"), "*3\r\n$3\r\nSET\r\n$1\r\nk\r\n$1\r\nv\r\n"},
		{"aninhado", NovoArray(NovoInteiro(1), NovoArray(NovoSimples("x"), BulkNulo())), "*2\r\n:1\r\n*2\r\n+x\r\n$-1\r\n"},
		{"utf8 conta bytes", NovoBulk("çã"), "$4\r\nçã\r\n"},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			b, err := Marshal(c.v)
			if err != nil || string(b) != c.quer {
				t.Fatalf("got %q err %v, quer %q", b, err, c.quer)
			}
		})
	}
}

func TestCodificarErros(t *testing.T) {
	for _, v := range []Valor{NovoSimples("a\nb"), NovoErro("a\rb"), NovoArray(NovoSimples("x\n"))} {
		if _, err := Marshal(v); err != ErrQuebraDeLinha {
			t.Errorf("%+v: err = %v", v, err)
		}
	}
	if _, err := Marshal(Valor{Tipo: '?'}); !errors.Is(err, ErrProtocolo) {
		t.Errorf("tipo desconhecido: %v", err)
	}
	var w bytes.Buffer
	if err := Codificar(&w, NovoInteiro(7)); err != nil || w.String() != ":7\r\n" {
		t.Errorf("Codificar: %q %v", w.String(), err)
	}
}

func dec(s string) (Valor, error) { return Decodificar(bufio.NewReader(strings.NewReader(s))) }

func TestIdaEVolta(t *testing.T) {
	casos := []Valor{
		NovoSimples("PONG"), NovoErro("WRONGTYPE x"), NovoInteiro(0), NovoInteiro(-9223372036854775808),
		NovoBulk(""), NovoBulk("com\r\nquebras\r\n"), NovoBulk(strings.Repeat("x", 100000)),
		BulkNulo(), ArrayNulo(), NovoArray(),
		NovoArray(NovoBulk("a"), NovoInteiro(5), NovoArray(NovoArray(BulkNulo()), NovoSimples("ok"))),
	}
	for i, v := range casos {
		b, err := Marshal(v)
		if err != nil {
			t.Fatal(err)
		}
		got, err := Decodificar(bufio.NewReader(bytes.NewReader(b)))
		if err != nil {
			t.Fatalf("caso %d: %v", i, err)
		}
		if !reflect.DeepEqual(normaliza(got), normaliza(v)) {
			t.Fatalf("caso %d: got %+v, quer %+v", i, got, v)
		}
	}
}

// normaliza trata array vazio nil e não nil como iguais.
func normaliza(v Valor) Valor {
	if v.Tipo == Array && len(v.Itens) == 0 {
		v.Itens = nil
	}
	for i := range v.Itens {
		v.Itens[i] = normaliza(v.Itens[i])
	}
	return v
}

func TestDecodificarVariosEmSequencia(t *testing.T) {
	r := bufio.NewReader(strings.NewReader("+OK\r\n:5\r\n$3\r\nabc\r\n"))
	var tipos []Tipo
	for {
		v, err := Decodificar(r)
		if err == io.EOF {
			break
		}
		if err != nil {
			t.Fatal(err)
		}
		tipos = append(tipos, v.Tipo)
	}
	if !reflect.DeepEqual(tipos, []Tipo{Simples, Inteiro, Bulk}) {
		t.Fatalf("tipos = %q", tipos)
	}
}

func TestDecodificarEntradaIncompleta(t *testing.T) {
	casos := []string{
		"+OK", "+OK\r", ":12", "$3\r\nab", "$3\r\nabc", "$3\r\nabc\r", "*2\r\n:1\r\n", "*3\r\n", "$",
	}
	for _, c := range casos {
		t.Run(c, func(t *testing.T) {
			_, err := dec(c)
			if err != io.ErrUnexpectedEOF {
				t.Fatalf("err = %v, quer ErrUnexpectedEOF", err)
			}
		})
	}
	if _, err := dec(""); err != io.EOF {
		t.Fatalf("vazio: %v", err)
	}
}

func TestDecodificarMalformado(t *testing.T) {
	casos := []struct {
		nome string
		in   string
	}{
		{"tipo desconhecido", "?abc\r\n"},
		{"so LF", "+OK\n"},
		{"inteiro invalido", ":abc\r\n"},
		{"inteiro estoura", ":99999999999999999999\r\n"},
		{"bulk tamanho invalido", "$abc\r\n"},
		{"bulk negativo", "$-2\r\n"},
		{"bulk gigante", "$99999999999\r\n"},
		{"bulk sem crlf", "$3\r\nabcXY"},
		{"array tamanho invalido", "*x\r\n"},
		{"array negativo", "*-5\r\n"},
		{"array enorme", "*99999999\r\n"},
		{"item invalido dentro do array", "*2\r\n:1\r\n?\r\n"},
		{"linha longa", "+" + strings.Repeat("a", 10000) + "\r\n"},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if _, err := dec(c.in); !errors.Is(err, ErrProtocolo) {
				t.Fatalf("err = %v", err)
			}
		})
	}
}

func TestProfundidadeMaxima(t *testing.T) {
	ok := strings.Repeat("*1\r\n", MaxProfundidade) + ":1\r\n"
	if _, err := dec(ok); err != nil {
		t.Fatalf("no limite: %v", err)
	}
	demais := strings.Repeat("*1\r\n", MaxProfundidade+5) + ":1\r\n"
	if _, err := dec(demais); !errors.Is(err, ErrProtocolo) {
		t.Fatalf("err = %v", err)
	}
}

func TestArgumentos(t *testing.T) {
	got, err := ComandoEmArray("GET", "chave").Argumentos()
	if err != nil || !reflect.DeepEqual(got, []string{"GET", "chave"}) {
		t.Fatalf("got %v %v", got, err)
	}
	invalidos := []Valor{NovoBulk("x"), ArrayNulo(), NovoArray(NovoInteiro(1)), NovoArray(BulkNulo())}
	for _, v := range invalidos {
		if _, err := v.Argumentos(); !errors.Is(err, ErrProtocolo) {
			t.Errorf("%+v: err = %v", v, err)
		}
	}
}

func TestLeituraEmFluxoFragmentado(t *testing.T) {
	// um leitor que entrega 1 byte por vez deve produzir o mesmo valor
	b, _ := Marshal(ComandoEmArray("SET", "chave", strings.Repeat("v", 5000)))
	r := bufio.NewReader(&umPorVez{b: b})
	v, err := Decodificar(r)
	if err != nil {
		t.Fatal(err)
	}
	args, _ := v.Argumentos()
	if len(args) != 3 || len(args[2]) != 5000 {
		t.Fatalf("args = %d itens", len(args))
	}
}

type umPorVez struct{ b []byte }

func (u *umPorVez) Read(p []byte) (int, error) {
	if len(u.b) == 0 {
		return 0, io.EOF
	}
	p[0] = u.b[0]
	u.b = u.b[1:]
	return 1, nil
}
