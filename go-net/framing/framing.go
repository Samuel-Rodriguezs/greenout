// Pacote framing delimita mensagens em fluxos de bytes (como o TCP):
// por prefixo de tamanho (4 bytes big endian) e por delimitador com
// byte stuffing no estilo SLIP (RFC 1055).
package framing

import (
	"bufio"
	"encoding/binary"
	"errors"
	"fmt"
	"io"
)

// Erros de enquadramento.
var (
	ErrQuadroGrande   = errors.New("framing: quadro excede o limite")
	ErrEscapeInvalido = errors.New("framing: sequência de escape inválida")
)

// EscreverTamanho escreve payload precedido de seu tamanho em 4 bytes.
func EscreverTamanho(w io.Writer, payload []byte) error {
	if uint64(len(payload)) > 0xFFFFFFFF {
		return ErrQuadroGrande
	}
	buf := make([]byte, 4+len(payload))
	binary.BigEndian.PutUint32(buf, uint32(len(payload)))
	copy(buf[4:], payload)
	_, err := w.Write(buf) // uma única escrita evita intercalar quadros
	return err
}

// LerTamanho lê um quadro com prefixo de tamanho. Devolve io.EOF se o fluxo
// terminou limpo entre quadros e io.ErrUnexpectedEOF se terminou no meio de um.
// Quadros maiores que max são recusados antes de alocar memória.
func LerTamanho(r io.Reader, max uint32) ([]byte, error) {
	var cab [4]byte
	if _, err := io.ReadFull(r, cab[:]); err != nil {
		return nil, err // EOF puro ou ErrUnexpectedEOF
	}
	n := binary.BigEndian.Uint32(cab[:])
	if n > max {
		return nil, fmt.Errorf("%w: %d > %d", ErrQuadroGrande, n, max)
	}
	buf := make([]byte, n)
	if _, err := io.ReadFull(r, buf); err != nil {
		if err == io.EOF {
			err = io.ErrUnexpectedEOF
		}
		return nil, err
	}
	return buf, nil
}

// Bytes especiais do SLIP.
const (
	slipEnd    = 0xC0
	slipEsc    = 0xDB
	slipEscEnd = 0xDC
	slipEscEsc = 0xDD
)

// EscreverSLIP escreve payload com byte stuffing, terminado por END (0xC0).
func EscreverSLIP(w io.Writer, payload []byte) error {
	buf := make([]byte, 0, len(payload)+8)
	for _, b := range payload {
		switch b {
		case slipEnd:
			buf = append(buf, slipEsc, slipEscEnd)
		case slipEsc:
			buf = append(buf, slipEsc, slipEscEsc)
		default:
			buf = append(buf, b)
		}
	}
	buf = append(buf, slipEnd)
	_, err := w.Write(buf)
	return err
}

// LerSLIP lê um quadro SLIP. Quadros vazios (END repetido) são ignorados.
// Devolve io.EOF se o fluxo acabou entre quadros e io.ErrUnexpectedEOF se
// acabou antes do END final. max limita o tamanho do quadro decodificado.
func LerSLIP(r *bufio.Reader, max int) ([]byte, error) {
	var quadro []byte
	for {
		b, err := r.ReadByte()
		if err != nil {
			if err == io.EOF && len(quadro) > 0 {
				err = io.ErrUnexpectedEOF
			}
			return nil, err
		}
		switch b {
		case slipEnd:
			if len(quadro) == 0 {
				continue
			}
			return quadro, nil
		case slipEsc:
			c, err := r.ReadByte()
			if err != nil {
				if err == io.EOF {
					err = io.ErrUnexpectedEOF
				}
				return nil, err
			}
			switch c {
			case slipEscEnd:
				b = slipEnd
			case slipEscEsc:
				b = slipEsc
			default:
				return nil, fmt.Errorf("%w: 0xDB 0x%02X", ErrEscapeInvalido, c)
			}
		}
		if len(quadro) >= max {
			return nil, fmt.Errorf("%w: mais de %d bytes", ErrQuadroGrande, max)
		}
		quadro = append(quadro, b)
	}
}
