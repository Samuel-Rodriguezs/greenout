// Pacote ipv4 implementa parse e formatação próprios de endereços IPv4.
package ipv4

import (
	"errors"
	"fmt"
	"strconv"
	"strings"
)

// Endereco é um endereço IPv4 de 32 bits em ordem de rede (big endian).
type Endereco uint32

// ErrFormato indica texto que não é um IPv4 válido em notação decimal pontuada.
var ErrFormato = errors.New("ipv4: formato inválido")

// Parse converte "a.b.c.d" em Endereco. Exige exatamente quatro octetos
// decimais de 0 a 255, sem sinais, espaços ou zeros à esquerda.
func Parse(s string) (Endereco, error) {
	partes := strings.Split(s, ".")
	if len(partes) != 4 {
		return 0, fmt.Errorf("%w: %q", ErrFormato, s)
	}
	var e Endereco
	for _, p := range partes {
		if p == "" || len(p) > 3 || (len(p) > 1 && p[0] == '0') {
			return 0, fmt.Errorf("%w: %q", ErrFormato, s)
		}
		for i := 0; i < len(p); i++ {
			if p[i] < '0' || p[i] > '9' {
				return 0, fmt.Errorf("%w: %q", ErrFormato, s)
			}
		}
		n, _ := strconv.Atoi(p)
		if n > 255 {
			return 0, fmt.Errorf("%w: octeto %d fora do intervalo", ErrFormato, n)
		}
		e = e<<8 | Endereco(n)
	}
	return e, nil
}

// MustParse é como Parse, mas entra em pânico em caso de erro (útil em testes).
func MustParse(s string) Endereco {
	e, err := Parse(s)
	if err != nil {
		panic(err)
	}
	return e
}

// DeOctetos monta um Endereco a partir de quatro octetos.
func DeOctetos(b [4]byte) Endereco {
	return Endereco(b[0])<<24 | Endereco(b[1])<<16 | Endereco(b[2])<<8 | Endereco(b[3])
}

// Octetos devolve os quatro octetos do endereço.
func (e Endereco) Octetos() [4]byte {
	return [4]byte{byte(e >> 24), byte(e >> 16), byte(e >> 8), byte(e)}
}

// String formata em notação decimal pontuada.
func (e Endereco) String() string {
	o := e.Octetos()
	return strconv.Itoa(int(o[0])) + "." + strconv.Itoa(int(o[1])) + "." +
		strconv.Itoa(int(o[2])) + "." + strconv.Itoa(int(o[3]))
}

// EhPrivado informa se o endereço está em 10/8, 172.16/12 ou 192.168/16 (RFC 1918).
func (e Endereco) EhPrivado() bool {
	return e>>24 == 10 || e>>20 == 0xAC1 || e>>16 == 0xC0A8
}

// EhLoopback informa se o endereço está em 127/8.
func (e Endereco) EhLoopback() bool { return e>>24 == 127 }

// EhMulticast informa se o endereço está em 224/4.
func (e Endereco) EhMulticast() bool { return e>>28 == 0xE }

// EhLinkLocal informa se o endereço está em 169.254/16.
func (e Endereco) EhLinkLocal() bool { return e>>16 == 0xA9FE }
