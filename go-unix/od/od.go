// Pacote od implementa uma versão simplificada do utilitário Unix od:
// despeja bytes, 16 por linha, com deslocamentos em octal.
package od

import (
	"fmt"
	"io"
	"strings"
)

// Formato escolhe como cada byte é exibido.
type Formato int

const (
	Octal Formato = iota // -b: bytes em octal (padrão)
	Hexa                 // -x: bytes em hexadecimal
	Chars                // -c: caracteres, com escapes
)

const bytesPorLinha = 16

// Caractere formata um byte para o modo -c.
func Caractere(b byte) string {
	switch b {
	case 0:
		return `\0`
	case '\a':
		return `\a`
	case '\b':
		return `\b`
	case '\t':
		return `\t`
	case '\n':
		return `\n`
	case '\v':
		return `\v`
	case '\f':
		return `\f`
	case '\r':
		return `\r`
	}
	if b >= 0x20 && b < 0x7f {
		return string(rune(b))
	}
	return fmt.Sprintf("%03o", b)
}

// Despejar devolve as linhas do despejo. A última linha contém somente o
// deslocamento final (total de bytes), como no od real.
func Despejar(dados []byte, f Formato) []string {
	var linhas []string
	for ini := 0; ini < len(dados); ini += bytesPorLinha {
		fim := ini + bytesPorLinha
		if fim > len(dados) {
			fim = len(dados)
		}
		var b strings.Builder
		fmt.Fprintf(&b, "%07o", ini)
		for _, x := range dados[ini:fim] {
			switch f {
			case Hexa:
				fmt.Fprintf(&b, " %02x", x)
			case Chars:
				fmt.Fprintf(&b, " %3s", Caractere(x))
			default:
				fmt.Fprintf(&b, " %03o", x)
			}
		}
		linhas = append(linhas, b.String())
	}
	return append(linhas, fmt.Sprintf("%07o", len(dados)))
}

// Executar interpreta [-b] [-x] [-c] (o último formato informado vence).
func Executar(args []string, in io.Reader, out io.Writer) error {
	f := Octal
	for _, a := range args {
		switch a {
		case "-b":
			f = Octal
		case "-x":
			f = Hexa
		case "-c":
			f = Chars
		default:
			return fmt.Errorf("od: argumento inválido %q", a)
		}
	}
	dados, err := io.ReadAll(in)
	if err != nil {
		return err
	}
	for _, l := range Despejar(dados, f) {
		if _, err := fmt.Fprintln(out, l); err != nil {
			return err
		}
	}
	return nil
}
