// Pacote checksum implementa o checksum de Internet (RFC 1071): soma em
// complemento de um de palavras de 16 bits, usada em IPv4, ICMP, UDP e TCP.
package checksum

// Soma devolve a soma em complemento de um (sem inverter) dos dados,
// tratados como palavras de 16 bits big endian. Se o tamanho for ímpar,
// o último byte é completado com zero à direita.
func Soma(dados []byte) uint16 { return dobra(soma32(0, dados)) }

func soma32(acc uint32, dados []byte) uint32 {
	n := len(dados)
	for i := 0; i+1 < n; i += 2 {
		acc += uint32(dados[i])<<8 | uint32(dados[i+1])
	}
	if n%2 == 1 {
		acc += uint32(dados[n-1]) << 8
	}
	return acc
}

// dobra incorpora os carries (end-around carry) de um acumulador de 32 bits.
func dobra(acc uint32) uint16 {
	for acc>>16 != 0 {
		acc = acc&0xFFFF + acc>>16
	}
	return uint16(acc)
}

// Calcular devolve o checksum de Internet (complemento da soma) dos dados.
// Para gerar um cabeçalho, zere o campo de checksum antes de chamar.
func Calcular(dados []byte) uint16 { return ^Soma(dados) }

// CalcularVarios calcula o checksum sobre a concatenação lógica de vários
// blocos (ex.: pseudo-cabeçalho + segmento), sem copiá-los. Cada bloco, exceto
// o último, deve ter tamanho par para que o pareamento de bytes seja correto.
func CalcularVarios(blocos ...[]byte) uint16 {
	var acc uint32
	for _, b := range blocos {
		acc += uint32(Soma(b))
	}
	return ^dobra(acc)
}

// Verifica informa se os dados, incluindo o campo de checksum preenchido, são
// consistentes: a soma em complemento de um deve resultar em 0xFFFF.
func Verifica(dados []byte) bool { return Soma(dados) == 0xFFFF }

// Atualizar recalcula incrementalmente um checksum quando uma palavra de 16
// bits muda de antigo para novo (RFC 1624, eq. 3), sem reler o pacote.
func Atualizar(cks, antigo, novo uint16) uint16 {
	acc := uint32(^cks) + uint32(^antigo) + uint32(novo)
	return ^dobra(acc)
}
