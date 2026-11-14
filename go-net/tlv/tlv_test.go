package tlv

import (
	"bytes"
	"errors"
	"reflect"
	"testing"
)

func TestCodificarVetores(t *testing.T) {
	casos := []struct {
		nome string
		item Item
		want []byte
	}{
		{"vazio", Item{0x01, nil}, []byte{0x01, 0x00}},
		{"curto", Item{0x02, []byte("oi")}, []byte{0x02, 0x02, 'o', 'i'}},
		{"127", Item{0x03, make([]byte, 127)}, append([]byte{0x03, 0x7F}, make([]byte, 127)...)},
		{"128", Item{0x04, make([]byte, 128)}, append([]byte{0x04, 0x81, 0x80}, make([]byte, 128)...)},
		{"300", Item{0x05, make([]byte, 300)}, append([]byte{0x05, 0x82, 0x01, 0x2C}, make([]byte, 300)...)},
		{"70000", Item{0x06, make([]byte, 70000)}, append([]byte{0x06, 0x83, 0x01, 0x11, 0x70}, make([]byte, 70000)...)},
	}
	for _, c := range casos {
		got, err := Codificar([]Item{c.item})
		if err != nil || !bytes.Equal(got, c.want) {
			t.Errorf("%s: err=%v, cabeçalho %x", c.nome, err, got[:min(len(got), 6)])
			continue
		}
		it, resto, err := DecodificarUm(got)
		if err != nil || len(resto) != 0 || it.Tipo != c.item.Tipo || !bytes.Equal(it.Valor, c.item.Valor) {
			t.Errorf("%s: ida e volta falhou: %v", c.nome, err)
		}
	}
}

func TestSequencia(t *testing.T) {
	itens := []Item{{1, []byte("a")}, {2, nil}, {3, bytes.Repeat([]byte{7}, 200)}, {1, []byte("b")}}
	b, err := Codificar(itens)
	if err != nil {
		t.Fatal(err)
	}
	got, err := Decodificar(b)
	if err != nil || !reflect.DeepEqual(got[0], itens[0]) || len(got) != 4 || !bytes.Equal(got[2].Valor, itens[2].Valor) {
		t.Fatalf("Decodificar: %v %v", got, err)
	}
	if it, ok := Buscar(got, 1); !ok || string(it.Valor) != "a" {
		t.Errorf("Buscar devolveu %v %v", it, ok)
	}
	if _, ok := Buscar(got, 99); ok {
		t.Error("Buscar de tipo ausente")
	}
}

func TestDecodificarVazio(t *testing.T) {
	itens, err := Decodificar(nil)
	if err != nil || len(itens) != 0 {
		t.Errorf("%v %v", itens, err)
	}
}

func TestDecodificarMalformado(t *testing.T) {
	casos := []struct {
		nome string
		dado []byte
		erro error
	}{
		{"so tipo", []byte{1}, ErrTruncado},
		{"valor curto", []byte{1, 5, 'a', 'b'}, ErrTruncado},
		{"comprimento longo truncado", []byte{1, 0x82, 0x01}, ErrTruncado},
		{"comprimento indefinido", []byte{1, 0x80}, ErrComprimento},
		{"comprimento > 4 bytes", []byte{1, 0x85, 1, 0, 0, 0, 0}, ErrComprimento},
		{"nao minimal (cabe na forma curta)", []byte{1, 0x81, 0x05, 1, 2, 3, 4, 5}, ErrComprimento},
		{"zero a esquerda", []byte{1, 0x82, 0x00, 0xFF, 0}, ErrComprimento},
		{"comprimento gigante", []byte{1, 0x84, 0xFF, 0xFF, 0xFF, 0xFF}, ErrGrande},
		{"item bom e lixo", []byte{1, 1, 'a', 9}, ErrTruncado},
	}
	for _, c := range casos {
		if _, err := Decodificar(c.dado); !errors.Is(err, c.erro) {
			t.Errorf("%s: err=%v, esperava %v", c.nome, err, c.erro)
		}
	}
}

func TestDecodificarCopiaValor(t *testing.T) {
	b := []byte{1, 2, 'x', 'y'}
	it, _, _ := DecodificarUm(b)
	b[2] = 'Z'
	if string(it.Valor) != "xy" {
		t.Error("Valor deveria ser uma cópia")
	}
}
