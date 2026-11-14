// Pacote codificacao reimplementa codificações comuns de protocolos:
// Base64 (RFC 4648), hexadecimal e inteiros de tamanho variável (varint/LEB128
// com zigzag para sinalizados).
package codificacao

import (
	"errors"
	"fmt"
)

// Erros de decodificação.
var (
	ErrCaractere = errors.New("codificacao: caractere inválido")
	ErrTamanho   = errors.New("codificacao: tamanho inválido")
	ErrTruncado  = errors.New("codificacao: varint truncado")
	ErrOverflow  = errors.New("codificacao: varint excede 64 bits")
)

const alfabetoBase64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

// Base64 codifica dados com o alfabeto padrão e preenchimento '='.
func Base64(dados []byte) string {
	saida := make([]byte, 0, (len(dados)+2)/3*4)
	for i := 0; i < len(dados); i += 3 {
		var v uint32
		n := min(3, len(dados)-i)
		for j := 0; j < 3; j++ {
			v <<= 8
			if j < n {
				v |= uint32(dados[i+j])
			}
		}
		saida = append(saida,
			alfabetoBase64[v>>18&63], alfabetoBase64[v>>12&63],
			'=', '=')
		tam := len(saida)
		if n >= 2 {
			saida[tam-2] = alfabetoBase64[v>>6&63]
		}
		if n == 3 {
			saida[tam-1] = alfabetoBase64[v&63]
		}
	}
	return string(saida)
}

// DecodificarBase64 é o inverso estrito de Base64: exige tamanho múltiplo de
// 4, preenchimento só no final e bits residuais zerados (forma canônica).
func DecodificarBase64(s string) ([]byte, error) {
	if len(s)%4 != 0 {
		return nil, fmt.Errorf("%w: %d não é múltiplo de 4", ErrTamanho, len(s))
	}
	var tabela [256]int8
	for i := range tabela {
		tabela[i] = -1
	}
	for i := 0; i < len(alfabetoBase64); i++ {
		tabela[alfabetoBase64[i]] = int8(i)
	}
	saida := make([]byte, 0, len(s)/4*3)
	for i := 0; i < len(s); i += 4 {
		bloco := s[i : i+4]
		ultimo := i+4 == len(s)
		pad := 0
		if ultimo {
			for pad < 2 && bloco[3-pad] == '=' {
				pad++
			}
		}
		var v uint32
		for j := 0; j < 4-pad; j++ {
			d := tabela[bloco[j]]
			if d < 0 {
				return nil, fmt.Errorf("%w: %q na posição %d", ErrCaractere, bloco[j], i+j)
			}
			v = v<<6 | uint32(d)
		}
		v <<= 6 * uint(pad)
		switch pad {
		case 0:
			saida = append(saida, byte(v>>16), byte(v>>8), byte(v))
		case 1:
			if v&0xFF != 0 {
				return nil, fmt.Errorf("%w: bits residuais não nulos", ErrCaractere)
			}
			saida = append(saida, byte(v>>16), byte(v>>8))
		case 2:
			if v&0xFFFF != 0 {
				return nil, fmt.Errorf("%w: bits residuais não nulos", ErrCaractere)
			}
			saida = append(saida, byte(v>>16))
		}
	}
	return saida, nil
}

// Hex codifica dados em hexadecimal minúsculo.
func Hex(dados []byte) string {
	const dig = "0123456789abcdef"
	saida := make([]byte, 0, 2*len(dados))
	for _, b := range dados {
		saida = append(saida, dig[b>>4], dig[b&15])
	}
	return string(saida)
}

// DecodificarHex lê hexadecimal em maiúsculas ou minúsculas.
func DecodificarHex(s string) ([]byte, error) {
	if len(s)%2 != 0 {
		return nil, fmt.Errorf("%w: %d dígitos", ErrTamanho, len(s))
	}
	saida := make([]byte, len(s)/2)
	for i := range saida {
		h, ok1 := valorHex(s[2*i])
		l, ok2 := valorHex(s[2*i+1])
		if !ok1 || !ok2 {
			return nil, fmt.Errorf("%w: na posição %d", ErrCaractere, 2*i)
		}
		saida[i] = h<<4 | l
	}
	return saida, nil
}

func valorHex(c byte) (byte, bool) {
	switch {
	case c >= '0' && c <= '9':
		return c - '0', true
	case c >= 'a' && c <= 'f':
		return c - 'a' + 10, true
	case c >= 'A' && c <= 'F':
		return c - 'A' + 10, true
	}
	return 0, false
}

// AcrescentarVarint acrescenta v a dst em LEB128 sem sinal (7 bits por byte,
// bit alto indica continuação).
func AcrescentarVarint(dst []byte, v uint64) []byte {
	for v >= 0x80 {
		dst = append(dst, byte(v)|0x80)
		v >>= 7
	}
	return append(dst, byte(v))
}

// LerVarint decodifica um varint no início de b e devolve o valor e quantos
// bytes foram consumidos. Rejeita valores que ultrapassam 64 bits.
func LerVarint(b []byte) (uint64, int, error) {
	var v uint64
	for i, c := range b {
		if i == 10 || (i == 9 && c > 1) {
			return 0, 0, ErrOverflow
		}
		v |= uint64(c&0x7F) << (7 * uint(i))
		if c < 0x80 {
			return v, i + 1, nil
		}
	}
	return 0, 0, ErrTruncado
}

// Zigzag mapeia inteiros sinalizados para sem sinal de modo que valores de
// pequena magnitude fiquem pequenos: 0,-1,1,-2,2 -> 0,1,2,3,4.
func Zigzag(n int64) uint64 { return uint64(n<<1) ^ uint64(n>>63) }

// DesZigzag inverte Zigzag.
func DesZigzag(u uint64) int64 { return int64(u>>1) ^ -int64(u&1) }

// AcrescentarVarintSinal codifica n com zigzag + varint.
func AcrescentarVarintSinal(dst []byte, n int64) []byte {
	return AcrescentarVarint(dst, Zigzag(n))
}

// LerVarintSinal decodifica um inteiro sinalizado codificado com zigzag.
func LerVarintSinal(b []byte) (int64, int, error) {
	u, n, err := LerVarint(b)
	return DesZigzag(u), n, err
}
