// Pacote dns interpreta e monta mensagens DNS (RFC 1035): cabeçalho,
// perguntas, registros de recurso e compressão de nomes por ponteiros.
package dns

import (
	"encoding/binary"
	"errors"
	"fmt"
	"strings"
)

// Tipos e classes mais comuns.
const (
	TipoA     = 1
	TipoNS    = 2
	TipoCNAME = 5
	TipoMX    = 15
	TipoTXT   = 16
	TipoAAAA  = 28
	ClasseIN  = 1
)

// Erros de interpretação.
var (
	ErrCurto     = errors.New("dns: mensagem truncada")
	ErrPonteiro  = errors.New("dns: ponteiro de compressão inválido")
	ErrRotulo    = errors.New("dns: rótulo inválido")
	ErrNomeLongo = errors.New("dns: nome longo demais")
)

// Cabecalho é o cabeçalho fixo de 12 bytes.
type Cabecalho struct {
	ID             uint16
	Resposta       bool  // QR
	Opcode         uint8 // 4 bits
	AA, TC, RD, RA bool
	Rcode          uint8 // 4 bits
	QD, AN, NS, AR uint16
}

// Pergunta é uma entrada da seção de perguntas.
type Pergunta struct {
	Nome   string
	Tipo   uint16
	Classe uint16
}

// Registro é um registro de recurso (resposta, autoridade ou adicional).
type Registro struct {
	Nome   string
	Tipo   uint16
	Classe uint16
	TTL    uint32
	Dados  []byte // RDATA bruto; nomes internos (CNAME, NS, MX) vêm descomprimidos em Texto
	Texto  string // para CNAME/NS: o nome alvo; para A: endereço decimal
}

// Mensagem é uma mensagem DNS completa.
type Mensagem struct {
	Cabecalho   Cabecalho
	Perguntas   []Pergunta
	Respostas   []Registro
	Autoridades []Registro
	Adicionais  []Registro
}

func (c Cabecalho) flags() uint16 {
	var f uint16
	if c.Resposta {
		f |= 1 << 15
	}
	f |= uint16(c.Opcode&0xF) << 11
	for bit, v := range map[uint]bool{10: c.AA, 9: c.TC, 8: c.RD, 7: c.RA} {
		if v {
			f |= 1 << bit
		}
	}
	return f | uint16(c.Rcode&0xF)
}

func cabecalhoDe(b []byte) Cabecalho {
	f := binary.BigEndian.Uint16(b[2:])
	return Cabecalho{
		ID: binary.BigEndian.Uint16(b[0:]), Resposta: f&(1<<15) != 0, Opcode: uint8(f >> 11 & 0xF),
		AA: f&(1<<10) != 0, TC: f&(1<<9) != 0, RD: f&(1<<8) != 0, RA: f&(1<<7) != 0, Rcode: uint8(f & 0xF),
		QD: binary.BigEndian.Uint16(b[4:]), AN: binary.BigEndian.Uint16(b[6:]),
		NS: binary.BigEndian.Uint16(b[8:]), AR: binary.BigEndian.Uint16(b[10:]),
	}
}

// LerNome decodifica o nome que começa em off, seguindo ponteiros de
// compressão. Devolve o nome (sem ponto final; a raiz é ".") e o offset do
// byte seguinte ao nome no ponto de origem (ponteiro ocupa 2 bytes).
//
// Ponteiros só podem apontar para trás da posição em que aparecem, o que
// elimina laços; os limites de 63 bytes por rótulo e 255 por nome também valem.
func LerNome(msg []byte, off int) (string, int, error) {
	var rotulos []string
	proximo := -1 // offset de retorno, fixado no primeiro ponteiro
	total := 0
	pos := off
	for {
		if pos >= len(msg) {
			return "", 0, ErrCurto
		}
		n := int(msg[pos])
		switch n & 0xC0 {
		case 0x00:
			if n == 0 {
				if proximo < 0 {
					proximo = pos + 1
				}
				if len(rotulos) == 0 {
					return ".", proximo, nil
				}
				return strings.Join(rotulos, "."), proximo, nil
			}
			if pos+1+n > len(msg) {
				return "", 0, ErrCurto
			}
			total += n + 1
			if total > 254 {
				return "", 0, ErrNomeLongo
			}
			rotulos = append(rotulos, string(msg[pos+1:pos+1+n]))
			pos += 1 + n
		case 0xC0:
			if pos+1 >= len(msg) {
				return "", 0, ErrCurto
			}
			alvo := (n&0x3F)<<8 | int(msg[pos+1])
			if alvo >= pos {
				return "", 0, fmt.Errorf("%w: aponta para %d a partir de %d", ErrPonteiro, alvo, pos)
			}
			if proximo < 0 {
				proximo = pos + 2
			}
			pos = alvo
		default: // 0x40 e 0x80 são reservados
			return "", 0, fmt.Errorf("%w: byte de comprimento %#x", ErrRotulo, n)
		}
	}
}

func lerRegistro(msg []byte, off int) (Registro, int, error) {
	var r Registro
	nome, off, err := LerNome(msg, off)
	if err != nil {
		return r, 0, err
	}
	if off+10 > len(msg) {
		return r, 0, ErrCurto
	}
	r.Nome = nome
	r.Tipo = binary.BigEndian.Uint16(msg[off:])
	r.Classe = binary.BigEndian.Uint16(msg[off+2:])
	r.TTL = binary.BigEndian.Uint32(msg[off+4:])
	n := int(binary.BigEndian.Uint16(msg[off+8:]))
	off += 10
	if off+n > len(msg) {
		return r, 0, ErrCurto
	}
	r.Dados = append([]byte(nil), msg[off:off+n]...)
	switch {
	case r.Tipo == TipoA && n == 4:
		r.Texto = fmt.Sprintf("%d.%d.%d.%d", r.Dados[0], r.Dados[1], r.Dados[2], r.Dados[3])
	case r.Tipo == TipoCNAME || r.Tipo == TipoNS:
		if r.Texto, _, err = LerNome(msg, off); err != nil {
			return r, 0, err
		}
	}
	return r, off + n, nil
}

// Parse interpreta uma mensagem DNS completa.
func Parse(msg []byte) (Mensagem, error) {
	var m Mensagem
	if len(msg) < 12 {
		return m, ErrCurto
	}
	m.Cabecalho = cabecalhoDe(msg)
	off := 12
	for i := 0; i < int(m.Cabecalho.QD); i++ {
		nome, prox, err := LerNome(msg, off)
		if err != nil {
			return m, err
		}
		if prox+4 > len(msg) {
			return m, ErrCurto
		}
		m.Perguntas = append(m.Perguntas, Pergunta{nome,
			binary.BigEndian.Uint16(msg[prox:]), binary.BigEndian.Uint16(msg[prox+2:])})
		off = prox + 4
	}
	secoes := []struct {
		n    uint16
		dest *[]Registro
	}{{m.Cabecalho.AN, &m.Respostas}, {m.Cabecalho.NS, &m.Autoridades}, {m.Cabecalho.AR, &m.Adicionais}}
	for _, s := range secoes {
		for i := 0; i < int(s.n); i++ {
			r, prox, err := lerRegistro(msg, off)
			if err != nil {
				return m, err
			}
			*s.dest = append(*s.dest, r)
			off = prox
		}
	}
	return m, nil
}

// escritor monta mensagens comprimindo nomes repetidos.
type escritor struct {
	buf   []byte
	nomes map[string]int // sufixo (minúsculo) -> offset da primeira ocorrência
}

func (e *escritor) nome(n string) error {
	if n == "." || n == "" {
		e.buf = append(e.buf, 0)
		return nil
	}
	rotulos := strings.Split(strings.TrimSuffix(n, "."), ".")
	for i, r := range rotulos {
		if len(r) == 0 || len(r) > 63 {
			return fmt.Errorf("%w: %q", ErrRotulo, r)
		}
		sufixo := strings.ToLower(strings.Join(rotulos[i:], "."))
		if off, ok := e.nomes[sufixo]; ok {
			e.buf = binary.BigEndian.AppendUint16(e.buf, 0xC000|uint16(off))
			return nil
		}
		if len(e.buf) < 0x4000 {
			e.nomes[sufixo] = len(e.buf)
		}
		e.buf = append(e.buf, byte(len(r)))
		e.buf = append(e.buf, r...)
	}
	e.buf = append(e.buf, 0)
	if len(n) > 253 {
		return ErrNomeLongo
	}
	return nil
}

// Serializar monta a mensagem em formato de fio, comprimindo nomes de
// perguntas e de registros. Os contadores do cabeçalho são recalculados a
// partir das seções. CNAME e NS usam Texto como alvo (também comprimido);
// os demais tipos usam Dados.
func (m Mensagem) Serializar() ([]byte, error) {
	e := &escritor{nomes: map[string]int{}}
	c := m.Cabecalho
	c.QD, c.AN, c.NS, c.AR = uint16(len(m.Perguntas)), uint16(len(m.Respostas)), uint16(len(m.Autoridades)), uint16(len(m.Adicionais))
	e.buf = binary.BigEndian.AppendUint16(e.buf, c.ID)
	e.buf = binary.BigEndian.AppendUint16(e.buf, c.flags())
	for _, v := range []uint16{c.QD, c.AN, c.NS, c.AR} {
		e.buf = binary.BigEndian.AppendUint16(e.buf, v)
	}
	for _, p := range m.Perguntas {
		if err := e.nome(p.Nome); err != nil {
			return nil, err
		}
		e.buf = binary.BigEndian.AppendUint16(e.buf, p.Tipo)
		e.buf = binary.BigEndian.AppendUint16(e.buf, p.Classe)
	}
	for _, sec := range [][]Registro{m.Respostas, m.Autoridades, m.Adicionais} {
		for _, r := range sec {
			if err := e.nome(r.Nome); err != nil {
				return nil, err
			}
			e.buf = binary.BigEndian.AppendUint16(e.buf, r.Tipo)
			e.buf = binary.BigEndian.AppendUint16(e.buf, r.Classe)
			e.buf = binary.BigEndian.AppendUint32(e.buf, r.TTL)
			posTam := len(e.buf)
			e.buf = append(e.buf, 0, 0)
			if r.Tipo == TipoCNAME || r.Tipo == TipoNS {
				if err := e.nome(r.Texto); err != nil {
					return nil, err
				}
			} else {
				e.buf = append(e.buf, r.Dados...)
			}
			n := len(e.buf) - posTam - 2
			if n > 0xFFFF {
				return nil, ErrCurto
			}
			binary.BigEndian.PutUint16(e.buf[posTam:], uint16(n))
		}
	}
	return e.buf, nil
}
