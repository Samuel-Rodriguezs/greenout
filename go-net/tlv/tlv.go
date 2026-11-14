// Pacote tlv implementa um codec Type-Length-Value. O tipo ocupa 1 byte e o
// comprimento usa a codificação do BER/DER: valores até 127 em um byte; acima
// disso, 0x80|n seguido de n bytes big endian (n de 1 a 4).
package tlv

import (
	"errors"
	"fmt"
)

// Erros de decodificação.
var (
	ErrTruncado    = errors.New("tlv: dados truncados")
	ErrComprimento = errors.New("tlv: comprimento inválido")
	ErrGrande      = errors.New("tlv: valor grande demais")
)

// MaxValor é o maior valor aceito por item (limite de 4 bytes de comprimento
// restrito a 31 bits para ser seguro em plataformas de 32 bits).
const MaxValor = 1<<31 - 1

// Item é um elemento TLV.
type Item struct {
	Tipo  byte
	Valor []byte
}

// Codificar serializa os itens em sequência.
func Codificar(itens []Item) ([]byte, error) {
	var out []byte
	for _, it := range itens {
		var err error
		if out, err = Acrescentar(out, it); err != nil {
			return nil, err
		}
	}
	return out, nil
}

// Acrescentar serializa um item ao final de dst.
func Acrescentar(dst []byte, it Item) ([]byte, error) {
	n := len(it.Valor)
	if n > MaxValor {
		return nil, fmt.Errorf("%w: %d bytes", ErrGrande, n)
	}
	dst = append(dst, it.Tipo)
	if n < 0x80 {
		dst = append(dst, byte(n))
	} else {
		var tmp [4]byte
		k := 0
		for v := n; v > 0; v >>= 8 {
			k++
		}
		for i := 0; i < k; i++ {
			tmp[k-1-i] = byte(n >> (8 * uint(i)))
		}
		dst = append(dst, 0x80|byte(k))
		dst = append(dst, tmp[:k]...)
	}
	return append(dst, it.Valor...), nil
}

// DecodificarUm lê o primeiro item de b e devolve o restante dos bytes.
func DecodificarUm(b []byte) (Item, []byte, error) {
	if len(b) < 2 {
		return Item{}, nil, ErrTruncado
	}
	tipo := b[0]
	n := int(b[1])
	b = b[2:]
	if n >= 0x80 {
		k := n & 0x7F
		if k == 0 || k > 4 {
			return Item{}, nil, fmt.Errorf("%w: %d bytes de comprimento", ErrComprimento, k)
		}
		if len(b) < k {
			return Item{}, nil, ErrTruncado
		}
		n = 0
		for _, c := range b[:k] {
			n = n<<8 | int(c)
		}
		if n < 0 || n > MaxValor {
			return Item{}, nil, ErrGrande
		}
		if n < 0x80 || b[0] == 0 {
			return Item{}, nil, fmt.Errorf("%w: forma longa não minimal", ErrComprimento)
		}
		b = b[k:]
	}
	if len(b) < n {
		return Item{}, nil, ErrTruncado
	}
	return Item{Tipo: tipo, Valor: append([]byte(nil), b[:n]...)}, b[n:], nil
}

// Decodificar lê todos os itens de b. Falha se sobrar byte incompleto.
func Decodificar(b []byte) ([]Item, error) {
	var itens []Item
	for len(b) > 0 {
		it, resto, err := DecodificarUm(b)
		if err != nil {
			return nil, err
		}
		itens = append(itens, it)
		b = resto
	}
	return itens, nil
}

// Buscar devolve o primeiro item com o tipo dado.
func Buscar(itens []Item, tipo byte) (Item, bool) {
	for _, it := range itens {
		if it.Tipo == tipo {
			return it, true
		}
	}
	return Item{}, false
}
