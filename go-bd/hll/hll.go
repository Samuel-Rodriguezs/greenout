// Pacote hll implementa o HyperLogLog, um estimador de cardinalidade que
// conta elementos distintos com memória fixa (2^p registradores de 1 byte)
// e erro típico de cerca de 1,04/sqrt(2^p). Inclui a correção de intervalo
// pequeno (linear counting), mesclagem e serialização com checksum.
package hll

import (
	"encoding/binary"
	"errors"
	"hash/crc32"
	"math"
	"math/bits"
	"sync"
)

const (
	// PrecisaoMin e PrecisaoMax limitam p (registradores = 2^p).
	PrecisaoMin = 4
	PrecisaoMax = 16
)

var (
	// ErrPrecisao indica p fora de [PrecisaoMin, PrecisaoMax].
	ErrPrecisao = errors.New("hll: precisão fora do intervalo 4..16")
	// ErrIncompativel indica mesclagem entre precisões diferentes.
	ErrIncompativel = errors.New("hll: precisões diferentes")
	// ErrFormato indica bytes que não são um HLL válido.
	ErrFormato = errors.New("hll: dados inválidos")
)

// HLL é um HyperLogLog seguro para uso concorrente.
type HLL struct {
	mu   sync.RWMutex
	p    uint8
	regs []uint8
}

// Novo cria um HLL com 2^p registradores.
func Novo(p uint8) (*HLL, error) {
	if p < PrecisaoMin || p > PrecisaoMax {
		return nil, ErrPrecisao
	}
	return &HLL{p: p, regs: make([]uint8, 1<<p)}, nil
}

// hash64: FNV-1a seguido do finalizador do splitmix64 (boa dispersão dos bits altos).
func hash64(dado []byte) uint64 {
	h := uint64(14695981039346656037)
	for _, b := range dado {
		h ^= uint64(b)
		h *= 1099511628211
	}
	h += 0x9e3779b97f4a7c15
	h = (h ^ (h >> 30)) * 0xbf58476d1ce4e5b9
	h = (h ^ (h >> 27)) * 0x94d049bb133111eb
	return h ^ (h >> 31)
}

// Adicionar registra um elemento.
func (h *HLL) Adicionar(dado []byte) {
	x := hash64(dado)
	idx := x >> (64 - h.p)
	resto := x << h.p
	rank := uint8(bits.LeadingZeros64(resto)) + 1
	if max := 64 - h.p + 1; rank > max {
		rank = max
	}
	h.mu.Lock()
	if rank > h.regs[idx] {
		h.regs[idx] = rank
	}
	h.mu.Unlock()
}

// AdicionarString registra uma string.
func (h *HLL) AdicionarString(s string) { h.Adicionar([]byte(s)) }

// Estimativa devolve a cardinalidade estimada.
func (h *HLL) Estimativa() uint64 {
	h.mu.RLock()
	defer h.mu.RUnlock()
	m := float64(len(h.regs))
	soma := 0.0
	zeros := 0
	for _, r := range h.regs {
		soma += math.Ldexp(1, -int(r))
		if r == 0 {
			zeros++
		}
	}
	var alfa float64
	switch len(h.regs) {
	case 16:
		alfa = 0.673
	case 32:
		alfa = 0.697
	case 64:
		alfa = 0.709
	default:
		alfa = 0.7213 / (1 + 1.079/m)
	}
	est := alfa * m * m / soma
	if est <= 2.5*m && zeros > 0 {
		est = m * math.Log(m/float64(zeros)) // linear counting
	}
	return uint64(math.Round(est))
}

// Mesclar incorpora o outro HLL (união dos conjuntos observados).
func (h *HLL) Mesclar(o *HLL) error {
	if h == o {
		return nil
	}
	o.mu.RLock()
	defer o.mu.RUnlock()
	h.mu.Lock()
	defer h.mu.Unlock()
	if h.p != o.p {
		return ErrIncompativel
	}
	for i, r := range o.regs {
		if r > h.regs[i] {
			h.regs[i] = r
		}
	}
	return nil
}

// MarshalBinary serializa: [p][registradores][crc32].
func (h *HLL) MarshalBinary() ([]byte, error) {
	h.mu.RLock()
	defer h.mu.RUnlock()
	b := make([]byte, 0, 1+len(h.regs)+4)
	b = append(b, h.p)
	b = append(b, h.regs...)
	return binary.LittleEndian.AppendUint32(b, crc32.ChecksumIEEE(b)), nil
}

// Carregar reconstrói um HLL serializado.
func Carregar(b []byte) (*HLL, error) {
	if len(b) < 5 {
		return nil, ErrFormato
	}
	p := b[0]
	if p < PrecisaoMin || p > PrecisaoMax || len(b) != 1+(1<<p)+4 {
		return nil, ErrFormato
	}
	corpo := b[:len(b)-4]
	if binary.LittleEndian.Uint32(b[len(b)-4:]) != crc32.ChecksumIEEE(corpo) {
		return nil, ErrFormato
	}
	max := 64 - p + 1
	regs := append([]uint8(nil), corpo[1:]...)
	for _, r := range regs {
		if r > max {
			return nil, ErrFormato
		}
	}
	return &HLL{p: p, regs: regs}, nil
}
