package framing

import (
	"bufio"
	"bytes"
	"errors"
	"io"
	"net"
	"reflect"
	"testing"
)

func TestTamanhoBytes(t *testing.T) {
	var buf bytes.Buffer
	if err := EscreverTamanho(&buf, []byte("abc")); err != nil {
		t.Fatal(err)
	}
	if !bytes.Equal(buf.Bytes(), []byte{0, 0, 0, 3, 'a', 'b', 'c'}) {
		t.Errorf("bytes = %v", buf.Bytes())
	}
	got, err := LerTamanho(&buf, 100)
	if err != nil || string(got) != "abc" {
		t.Errorf("LerTamanho = %q %v", got, err)
	}
	if _, err := LerTamanho(&buf, 100); err != io.EOF {
		t.Errorf("fim limpo deveria ser io.EOF, veio %v", err)
	}
}

func TestTamanhoQuadrosVaziosEMultiplos(t *testing.T) {
	var buf bytes.Buffer
	msgs := [][]byte{{}, []byte("um"), {}, bytes.Repeat([]byte{9}, 1000)}
	for _, m := range msgs {
		if err := EscreverTamanho(&buf, m); err != nil {
			t.Fatal(err)
		}
	}
	for i, m := range msgs {
		got, err := LerTamanho(&buf, 5000)
		if err != nil || !bytes.Equal(got, m) {
			t.Fatalf("quadro %d: %v", i, err)
		}
	}
}

func TestTamanhoMalformado(t *testing.T) {
	casos := []struct {
		nome string
		dado []byte
		max  uint32
		erro error
	}{
		{"vazio", nil, 10, io.EOF},
		{"cabecalho parcial", []byte{0, 0}, 10, io.ErrUnexpectedEOF},
		{"corpo ausente", []byte{0, 0, 0, 5}, 10, io.ErrUnexpectedEOF},
		{"corpo parcial", []byte{0, 0, 0, 5, 1, 2}, 10, io.ErrUnexpectedEOF},
		{"acima do limite", []byte{0, 0, 0, 11}, 10, ErrQuadroGrande},
		{"tamanho gigante", []byte{0xFF, 0xFF, 0xFF, 0xFF}, 1 << 20, ErrQuadroGrande},
	}
	for _, c := range casos {
		if _, err := LerTamanho(bytes.NewReader(c.dado), c.max); !errors.Is(err, c.erro) {
			t.Errorf("%s: err=%v, esperava %v", c.nome, err, c.erro)
		}
	}
}

func TestSLIPVetores(t *testing.T) {
	casos := []struct {
		nome    string
		payload []byte
		fio     []byte
	}{
		{"simples", []byte("ab"), []byte{'a', 'b', 0xC0}},
		{"contem END", []byte{1, 0xC0, 2}, []byte{1, 0xDB, 0xDC, 2, 0xC0}},
		{"contem ESC", []byte{0xDB}, []byte{0xDB, 0xDD, 0xC0}},
		{"ESC seguido de DC literal", []byte{0xDB, 0xDC}, []byte{0xDB, 0xDD, 0xDC, 0xC0}},
		{"so END", []byte{0xC0, 0xC0}, []byte{0xDB, 0xDC, 0xDB, 0xDC, 0xC0}},
	}
	for _, c := range casos {
		var buf bytes.Buffer
		if err := EscreverSLIP(&buf, c.payload); err != nil || !bytes.Equal(buf.Bytes(), c.fio) {
			t.Errorf("%s: fio=%x err=%v", c.nome, buf.Bytes(), err)
		}
		got, err := LerSLIP(bufio.NewReader(&buf), 100)
		if err != nil || !bytes.Equal(got, c.payload) {
			t.Errorf("%s: LerSLIP = %x %v", c.nome, got, err)
		}
	}
}

func TestSLIPMalformado(t *testing.T) {
	casos := []struct {
		nome string
		dado []byte
		erro error
	}{
		{"vazio", nil, io.EOF},
		{"so delimitadores", []byte{0xC0, 0xC0, 0xC0}, io.EOF},
		{"sem END final", []byte{1, 2, 3}, io.ErrUnexpectedEOF},
		{"ESC no fim", []byte{1, 0xDB}, io.ErrUnexpectedEOF},
		{"escape invalido", []byte{0xDB, 0x01, 0xC0}, ErrEscapeInvalido},
		{"excede limite", bytes.Repeat([]byte{1}, 20), ErrQuadroGrande},
	}
	for _, c := range casos {
		if _, err := LerSLIP(bufio.NewReader(bytes.NewReader(c.dado)), 10); !errors.Is(err, c.erro) {
			t.Errorf("%s: err=%v, esperava %v", c.nome, err, c.erro)
		}
	}
}

func TestSLIPIgnoraQuadrosVazios(t *testing.T) {
	r := bufio.NewReader(bytes.NewReader([]byte{0xC0, 'a', 0xC0, 0xC0, 'b', 'c', 0xC0}))
	a, _ := LerSLIP(r, 10)
	b, _ := LerSLIP(r, 10)
	if string(a) != "a" || string(b) != "bc" {
		t.Errorf("a=%q b=%q", a, b)
	}
}

// Fluxo real entre duas pontas conectadas por net.Pipe (sem abrir portas).
func TestComNetPipe(t *testing.T) {
	msgs := [][]byte{[]byte("primeiro"), {}, {0xC0, 0xDB, 0xC0}, bytes.Repeat([]byte("x"), 4096)}

	t.Run("tamanho", func(t *testing.T) {
		cli, srv := net.Pipe()
		defer srv.Close()
		go func() {
			defer cli.Close()
			for _, m := range msgs {
				if err := EscreverTamanho(cli, m); err != nil {
					return
				}
			}
		}()
		var got [][]byte
		for {
			m, err := LerTamanho(srv, 1<<16)
			if err == io.EOF {
				break
			}
			if err != nil {
				t.Fatal(err)
			}
			got = append(got, m)
		}
		if !reflect.DeepEqual(got, msgs) {
			t.Errorf("recebidos %d quadros diferentes dos enviados", len(got))
		}
	})

	t.Run("slip", func(t *testing.T) {
		cli, srv := net.Pipe()
		defer srv.Close()
		go func() {
			defer cli.Close()
			for _, m := range msgs[:1] {
				EscreverSLIP(cli, m)
			}
			for _, m := range msgs[2:] {
				EscreverSLIP(cli, m)
			}
		}()
		br := bufio.NewReader(srv)
		var got [][]byte
		for {
			m, err := LerSLIP(br, 1<<16)
			if err == io.EOF {
				break
			}
			if err != nil {
				t.Fatal(err)
			}
			got = append(got, m)
		}
		want := [][]byte{msgs[0], msgs[2], msgs[3]}
		if !reflect.DeepEqual(got, want) {
			t.Errorf("recebidos %d quadros", len(got))
		}
	})
}
