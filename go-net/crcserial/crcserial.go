// Pacote crcserial serializa registros em um envelope binário protegido por
// CRC-32 (IEEE 802.3), com a tabela do CRC calculada pelo próprio pacote.
//
// Formato do envelope (big endian):
//
//	magic "GN" (2) | versão (1) | tamanho do corpo (4) | corpo | CRC32 de tudo o que precede (4)
package crcserial

import (
	"encoding/binary"
	"errors"
	"fmt"
	"io"
)

// Erros conhecidos.
var (
	ErrMagic  = errors.New("crcserial: magic inválido")
	ErrVersao = errors.New("crcserial: versão não suportada")
	ErrCurto  = errors.New("crcserial: dados truncados")
	ErrCRC    = errors.New("crcserial: CRC não confere")
	ErrGrande = errors.New("crcserial: campo grande demais")
)

const (
	versao       = 1
	tamCabecalho = 7
	// MaxCorpo é o maior corpo aceito por envelope.
	MaxCorpo = 1 << 24
)

// tabela do CRC-32 IEEE (polinômio refletido 0xEDB88320).
var tabela = func() (t [256]uint32) {
	for i := range t {
		c := uint32(i)
		for k := 0; k < 8; k++ {
			if c&1 == 1 {
				c = c>>1 ^ 0xEDB88320
			} else {
				c >>= 1
			}
		}
		t[i] = c
	}
	return
}()

// CRC32 calcula o CRC-32 IEEE dos dados (o mesmo de zip, gzip e Ethernet).
func CRC32(dados []byte) uint32 { return Atualizar(0, dados) }

// Atualizar continua um CRC-32 já calculado (crc) com mais dados, permitindo
// processar fluxos em partes: Atualizar(CRC32(a), b) == CRC32(a+b).
func Atualizar(crc uint32, dados []byte) uint32 {
	c := ^crc
	for _, b := range dados {
		c = tabela[byte(c)^b] ^ c>>8
	}
	return ^c
}

// Selar envolve o corpo em um envelope com cabeçalho e CRC.
func Selar(corpo []byte) ([]byte, error) {
	if len(corpo) > MaxCorpo {
		return nil, fmt.Errorf("%w: corpo de %d bytes", ErrGrande, len(corpo))
	}
	b := make([]byte, 0, tamCabecalho+len(corpo)+4)
	b = append(b, 'G', 'N', versao)
	b = binary.BigEndian.AppendUint32(b, uint32(len(corpo)))
	b = append(b, corpo...)
	return binary.BigEndian.AppendUint32(b, CRC32(b)), nil
}

// Abrir valida um envelope completo e devolve o corpo. Bytes após o envelope
// são ignorados; use Ler para consumir de um fluxo.
func Abrir(b []byte) ([]byte, error) {
	if len(b) < tamCabecalho {
		return nil, ErrCurto
	}
	if b[0] != 'G' || b[1] != 'N' {
		return nil, ErrMagic
	}
	if b[2] != versao {
		return nil, fmt.Errorf("%w: %d", ErrVersao, b[2])
	}
	n := binary.BigEndian.Uint32(b[3:])
	if n > MaxCorpo {
		return nil, fmt.Errorf("%w: corpo de %d bytes", ErrGrande, n)
	}
	fim := tamCabecalho + int(n)
	if len(b) < fim+4 {
		return nil, ErrCurto
	}
	if CRC32(b[:fim]) != binary.BigEndian.Uint32(b[fim:]) {
		return nil, ErrCRC
	}
	return b[tamCabecalho:fim], nil
}

// Escrever grava um envelope no writer.
func Escrever(w io.Writer, corpo []byte) error {
	b, err := Selar(corpo)
	if err != nil {
		return err
	}
	_, err = w.Write(b)
	return err
}

// Ler lê exatamente um envelope do reader e devolve o corpo validado. Devolve
// io.EOF se o fluxo terminou limpo antes de qualquer byte.
func Ler(r io.Reader) ([]byte, error) {
	cab := make([]byte, tamCabecalho)
	if _, err := io.ReadFull(r, cab); err != nil {
		return nil, err
	}
	if cab[0] != 'G' || cab[1] != 'N' {
		return nil, ErrMagic
	}
	if cab[2] != versao {
		return nil, fmt.Errorf("%w: %d", ErrVersao, cab[2])
	}
	n := binary.BigEndian.Uint32(cab[3:])
	if n > MaxCorpo {
		return nil, fmt.Errorf("%w: corpo de %d bytes", ErrGrande, n)
	}
	resto := make([]byte, int(n)+4)
	if _, err := io.ReadFull(r, resto); err != nil {
		if err == io.EOF {
			err = io.ErrUnexpectedEOF
		}
		return nil, err
	}
	if Atualizar(CRC32(cab), resto[:n]) != binary.BigEndian.Uint32(resto[n:]) {
		return nil, ErrCRC
	}
	return resto[:n], nil
}

// Registro é um exemplo de estrutura serializável: identificador, nome e
// uma série de medições.
type Registro struct {
	ID      uint32
	Nome    string
	Valores []int32
}

// Marshal serializa o registro (sem envelope): ID(4) | len(nome)(2) | nome |
// len(valores)(2) | valores(4 cada).
func (r Registro) Marshal() ([]byte, error) {
	if len(r.Nome) > 0xFFFF || len(r.Valores) > 0xFFFF {
		return nil, ErrGrande
	}
	b := binary.BigEndian.AppendUint32(nil, r.ID)
	b = binary.BigEndian.AppendUint16(b, uint16(len(r.Nome)))
	b = append(b, r.Nome...)
	b = binary.BigEndian.AppendUint16(b, uint16(len(r.Valores)))
	for _, v := range r.Valores {
		b = binary.BigEndian.AppendUint32(b, uint32(v))
	}
	return b, nil
}

// UnmarshalRegistro interpreta o formato de Marshal; rejeita dados truncados
// ou com bytes sobrando.
func UnmarshalRegistro(b []byte) (Registro, error) {
	var r Registro
	if len(b) < 6 {
		return r, ErrCurto
	}
	r.ID = binary.BigEndian.Uint32(b)
	nn := int(binary.BigEndian.Uint16(b[4:]))
	b = b[6:]
	if len(b) < nn+2 {
		return r, ErrCurto
	}
	r.Nome = string(b[:nn])
	nv := int(binary.BigEndian.Uint16(b[nn:]))
	b = b[nn+2:]
	if len(b) != nv*4 {
		return r, fmt.Errorf("%w: esperava %d bytes de valores, há %d", ErrCurto, nv*4, len(b))
	}
	if nv > 0 {
		r.Valores = make([]int32, nv)
		for i := range r.Valores {
			r.Valores[i] = int32(binary.BigEndian.Uint32(b[4*i:]))
		}
	}
	return r, nil
}

// SelarRegistro serializa e sela um registro.
func SelarRegistro(r Registro) ([]byte, error) {
	corpo, err := r.Marshal()
	if err != nil {
		return nil, err
	}
	return Selar(corpo)
}

// AbrirRegistro valida o envelope e decodifica o registro.
func AbrirRegistro(b []byte) (Registro, error) {
	corpo, err := Abrir(b)
	if err != nil {
		return Registro{}, err
	}
	return UnmarshalRegistro(corpo)
}
