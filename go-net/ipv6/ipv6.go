// Pacote ipv6 implementa parse e formatação próprios de endereços IPv6
// (forma completa, comprimida com "::" e com sufixo IPv4 embutido).
package ipv6

import (
	"errors"
	"fmt"
	"strings"

	"greenout/net/ipv4"
)

// Endereco é um endereço IPv6 de 128 bits.
type Endereco [16]byte

// ErrFormato indica texto que não é um IPv6 válido.
var ErrFormato = errors.New("ipv6: formato inválido")

func erroFormato(s string) error { return fmt.Errorf("%w: %q", ErrFormato, s) }

func valorHex(c byte) int {
	switch {
	case c >= '0' && c <= '9':
		return int(c - '0')
	case c >= 'a' && c <= 'f':
		return int(c-'a') + 10
	case c >= 'A' && c <= 'F':
		return int(c-'A') + 10
	}
	return -1
}

// grupos converte uma lista separada por ":" em grupos de 16 bits. Se
// permiteV4 for verdadeiro, o último elemento pode ser um IPv4 (vale 2 grupos).
func grupos(s string, permiteV4 bool) ([]uint16, error) {
	if s == "" {
		return nil, nil
	}
	partes := strings.Split(s, ":")
	var out []uint16
	for i, p := range partes {
		if strings.Contains(p, ".") {
			if !permiteV4 || i != len(partes)-1 {
				return nil, erroFormato(s)
			}
			v4, err := ipv4.Parse(p)
			if err != nil {
				return nil, erroFormato(s)
			}
			out = append(out, uint16(v4>>16), uint16(v4))
			continue
		}
		if len(p) == 0 || len(p) > 4 {
			return nil, erroFormato(s)
		}
		var v int
		for j := 0; j < len(p); j++ {
			d := valorHex(p[j])
			if d < 0 {
				return nil, erroFormato(s)
			}
			v = v<<4 | d
		}
		out = append(out, uint16(v))
	}
	return out, nil
}

// Parse converte texto IPv6 em Endereco.
func Parse(s string) (Endereco, error) {
	var e Endereco
	var gs []uint16
	if idx := strings.Index(s, "::"); idx >= 0 {
		cabeca, cauda := s[:idx], s[idx+2:]
		if strings.Contains(cauda, "::") {
			return e, erroFormato(s)
		}
		h, err := grupos(cabeca, false)
		if err != nil {
			return e, err
		}
		t, err := grupos(cauda, true)
		if err != nil {
			return e, err
		}
		if len(h)+len(t) > 7 {
			return e, erroFormato(s)
		}
		gs = append(gs, h...)
		gs = append(gs, make([]uint16, 8-len(h)-len(t))...)
		gs = append(gs, t...)
	} else {
		var err error
		gs, err = grupos(s, true)
		if err != nil {
			return e, err
		}
		if len(gs) != 8 {
			return e, erroFormato(s)
		}
	}
	for i, g := range gs {
		e[2*i] = byte(g >> 8)
		e[2*i+1] = byte(g)
	}
	return e, nil
}

// MustParse é como Parse, mas entra em pânico em caso de erro.
func MustParse(s string) Endereco {
	e, err := Parse(s)
	if err != nil {
		panic(err)
	}
	return e
}

// Grupo devolve o i-ésimo grupo de 16 bits (0 a 7).
func (e Endereco) Grupo(i int) uint16 { return uint16(e[2*i])<<8 | uint16(e[2*i+1]) }

// String formata conforme a RFC 5952: minúsculas, sem zeros à esquerda e com
// a maior sequência (a primeira em caso de empate) de dois ou mais grupos
// nulos substituída por "::".
func (e Endereco) String() string {
	melhorIni, melhorTam := -1, 0
	for i := 0; i < 8; {
		if e.Grupo(i) != 0 {
			i++
			continue
		}
		j := i
		for j < 8 && e.Grupo(j) == 0 {
			j++
		}
		if j-i > melhorTam {
			melhorIni, melhorTam = i, j-i
		}
		i = j
	}
	if melhorTam < 2 {
		melhorIni = -1
	}
	const dig = "0123456789abcdef"
	var sb strings.Builder
	for i := 0; i < 8; i++ {
		if i == melhorIni {
			sb.WriteString("::")
			i += melhorTam - 1
			continue
		}
		if i > 0 && i != melhorIni+melhorTam {
			sb.WriteByte(':')
		}
		g := e.Grupo(i)
		escrito := false
		for sh := 12; sh >= 0; sh -= 4 {
			d := g >> uint(sh) & 0xF
			if d != 0 || escrito || sh == 0 {
				sb.WriteByte(dig[d])
				escrito = true
			}
		}
	}
	return sb.String()
}

// EhLoopback informa se o endereço é ::1.
func (e Endereco) EhLoopback() bool { return e == Endereco{15: 1} }

// EhNaoEspecificado informa se o endereço é ::.
func (e Endereco) EhNaoEspecificado() bool { return e == Endereco{} }

// EhLinkLocal informa se o endereço está em fe80::/10.
func (e Endereco) EhLinkLocal() bool { return e[0] == 0xFE && e[1]&0xC0 == 0x80 }

// EhUnicoLocal informa se o endereço está em fc00::/7.
func (e Endereco) EhUnicoLocal() bool { return e[0]&0xFE == 0xFC }

// IPv4Mapeado devolve o IPv4 contido em um endereço ::ffff:a.b.c.d.
func (e Endereco) IPv4Mapeado() (ipv4.Endereco, bool) {
	for i := 0; i < 10; i++ {
		if e[i] != 0 {
			return 0, false
		}
	}
	if e[10] != 0xFF || e[11] != 0xFF {
		return 0, false
	}
	return ipv4.DeOctetos([4]byte{e[12], e[13], e[14], e[15]}), true
}
