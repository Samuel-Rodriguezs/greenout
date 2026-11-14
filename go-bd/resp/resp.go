// Pacote resp implementa codificação e decodificação do protocolo de texto
// RESP (REdis Serialization Protocol, versão 2): strings simples (+),
// erros (-), inteiros (:), bulk strings ($) e arrays (*), incluindo os
// valores nulos ($-1 e *-1). A decodificação impõe limites de tamanho,
// quantidade e profundidade para resistir a entradas maliciosas.
package resp

import (
	"bufio"
	"bytes"
	"errors"
	"fmt"
	"io"
	"strconv"
	"strings"
)

// Limites de decodificação.
const (
	MaxBulk         = 64 << 20
	MaxElementos    = 1 << 20
	MaxProfundidade = 32
)

// Tipo é o byte inicial de cada valor RESP.
type Tipo byte

const (
	Simples Tipo = '+'
	Erro    Tipo = '-'
	Inteiro Tipo = ':'
	Bulk    Tipo = '$'
	Array   Tipo = '*'
)

var (
	// ErrProtocolo indica entrada que viola o formato RESP.
	ErrProtocolo = errors.New("resp: protocolo inválido")
	// ErrQuebraDeLinha indica texto com CR ou LF em string simples ou erro.
	ErrQuebraDeLinha = errors.New("resp: string simples não pode conter CR/LF")
)

// Valor é um valor RESP decodificado.
type Valor struct {
	Tipo  Tipo
	Str   string  // Simples, Erro e Bulk
	Int   int64   // Inteiro
	Itens []Valor // Array
	Nulo  bool    // Bulk ou Array nulo
}

// Construtores.
func NovoSimples(s string) Valor  { return Valor{Tipo: Simples, Str: s} }
func NovoErro(s string) Valor     { return Valor{Tipo: Erro, Str: s} }
func NovoInteiro(n int64) Valor   { return Valor{Tipo: Inteiro, Int: n} }
func NovoBulk(s string) Valor     { return Valor{Tipo: Bulk, Str: s} }
func BulkNulo() Valor             { return Valor{Tipo: Bulk, Nulo: true} }
func NovoArray(vs ...Valor) Valor { return Valor{Tipo: Array, Itens: vs} }
func ArrayNulo() Valor            { return Valor{Tipo: Array, Nulo: true} }

// ComandoEmArray monta o formato de requisição: array de bulk strings.
func ComandoEmArray(args ...string) Valor {
	itens := make([]Valor, len(args))
	for i, a := range args {
		itens[i] = NovoBulk(a)
	}
	return NovoArray(itens...)
}

// Argumentos extrai as strings de um array de bulks/simples.
func (v Valor) Argumentos() ([]string, error) {
	if v.Tipo != Array || v.Nulo {
		return nil, fmt.Errorf("%w: esperado array", ErrProtocolo)
	}
	out := make([]string, len(v.Itens))
	for i, it := range v.Itens {
		if (it.Tipo != Bulk && it.Tipo != Simples) || it.Nulo {
			return nil, fmt.Errorf("%w: argumento %d não é texto", ErrProtocolo, i)
		}
		out[i] = it.Str
	}
	return out, nil
}

// Codificar escreve o valor em w.
func Codificar(w io.Writer, v Valor) error {
	var buf bytes.Buffer
	if err := codificar(&buf, v); err != nil {
		return err
	}
	_, err := w.Write(buf.Bytes())
	return err
}

// Marshal devolve o valor codificado.
func Marshal(v Valor) ([]byte, error) {
	var buf bytes.Buffer
	if err := codificar(&buf, v); err != nil {
		return nil, err
	}
	return buf.Bytes(), nil
}

func codificar(b *bytes.Buffer, v Valor) error {
	switch v.Tipo {
	case Simples, Erro:
		if strings.ContainsAny(v.Str, "\r\n") {
			return ErrQuebraDeLinha
		}
		b.WriteByte(byte(v.Tipo))
		b.WriteString(v.Str)
		b.WriteString("\r\n")
	case Inteiro:
		b.WriteByte(':')
		b.WriteString(strconv.FormatInt(v.Int, 10))
		b.WriteString("\r\n")
	case Bulk:
		if v.Nulo {
			b.WriteString("$-1\r\n")
			return nil
		}
		b.WriteByte('$')
		b.WriteString(strconv.Itoa(len(v.Str)))
		b.WriteString("\r\n")
		b.WriteString(v.Str)
		b.WriteString("\r\n")
	case Array:
		if v.Nulo {
			b.WriteString("*-1\r\n")
			return nil
		}
		b.WriteByte('*')
		b.WriteString(strconv.Itoa(len(v.Itens)))
		b.WriteString("\r\n")
		for _, it := range v.Itens {
			if err := codificar(b, it); err != nil {
				return err
			}
		}
	default:
		return fmt.Errorf("%w: tipo %q desconhecido", ErrProtocolo, byte(v.Tipo))
	}
	return nil
}

// Decodificar lê um valor completo. Devolve io.EOF se a entrada terminou
// antes de qualquer byte e io.ErrUnexpectedEOF se terminou no meio de um valor.
func Decodificar(r *bufio.Reader) (Valor, error) {
	return decodificar(r, 0)
}

func linha(r *bufio.Reader) (string, error) {
	l, err := r.ReadSlice('\n')
	if err == bufio.ErrBufferFull {
		return "", fmt.Errorf("%w: linha longa demais", ErrProtocolo)
	}
	if err != nil {
		if err == io.EOF && len(l) > 0 {
			return "", io.ErrUnexpectedEOF
		}
		return "", err
	}
	if len(l) < 2 || l[len(l)-2] != '\r' {
		return "", fmt.Errorf("%w: linha sem CRLF", ErrProtocolo)
	}
	return string(l[:len(l)-2]), nil
}

func decodificar(r *bufio.Reader, nivel int) (Valor, error) {
	if nivel > MaxProfundidade {
		return Valor{}, fmt.Errorf("%w: aninhamento profundo demais", ErrProtocolo)
	}
	t, err := r.ReadByte()
	if err != nil {
		return Valor{}, err // io.EOF limpo
	}
	cab, err := linha(r)
	if err != nil {
		return Valor{}, eof(err)
	}
	switch Tipo(t) {
	case Simples:
		return Valor{Tipo: Simples, Str: cab}, nil
	case Erro:
		return Valor{Tipo: Erro, Str: cab}, nil
	case Inteiro:
		n, err := strconv.ParseInt(cab, 10, 64)
		if err != nil {
			return Valor{}, fmt.Errorf("%w: inteiro inválido %q", ErrProtocolo, cab)
		}
		return Valor{Tipo: Inteiro, Int: n}, nil
	case Bulk:
		n, err := strconv.ParseInt(cab, 10, 64)
		if err != nil || n < -1 || n > MaxBulk {
			return Valor{}, fmt.Errorf("%w: tamanho de bulk inválido %q", ErrProtocolo, cab)
		}
		if n == -1 {
			return BulkNulo(), nil
		}
		dados, err := io.ReadAll(io.LimitReader(r, n+2))
		if err != nil {
			return Valor{}, err
		}
		if int64(len(dados)) != n+2 {
			return Valor{}, io.ErrUnexpectedEOF
		}
		if dados[n] != '\r' || dados[n+1] != '\n' {
			return Valor{}, fmt.Errorf("%w: bulk sem CRLF final", ErrProtocolo)
		}
		return Valor{Tipo: Bulk, Str: string(dados[:n])}, nil
	case Array:
		n, err := strconv.ParseInt(cab, 10, 64)
		if err != nil || n < -1 || n > MaxElementos {
			return Valor{}, fmt.Errorf("%w: tamanho de array inválido %q", ErrProtocolo, cab)
		}
		if n == -1 {
			return ArrayNulo(), nil
		}
		itens := make([]Valor, 0, min(n, 1024))
		for i := int64(0); i < n; i++ {
			it, err := decodificar(r, nivel+1)
			if err != nil {
				return Valor{}, eof(err)
			}
			itens = append(itens, it)
		}
		return Valor{Tipo: Array, Itens: itens}, nil
	}
	return Valor{}, fmt.Errorf("%w: byte inicial %q", ErrProtocolo, t)
}

// eof converte EOF no meio de um valor em ErrUnexpectedEOF.
func eof(err error) error {
	if err == io.EOF {
		return io.ErrUnexpectedEOF
	}
	return err
}
