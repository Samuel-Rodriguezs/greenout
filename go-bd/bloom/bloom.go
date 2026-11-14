// Pacote bloom implementa um filtro de Bloom: estrutura probabilística que
// responde "talvez presente" ou "definitivamente ausente", sem falsos
// negativos. Usa hashing duplo (Kirsch-Mitzenmacher) sobre FNV-1a de 64 bits
// e serializa com checksum para ser guardado em arquivos.
package bloom

import (
	"encoding/binary"
	"errors"
	"hash/crc32"
	"math"
	"sync"
)

var (
	// ErrParametros indica capacidade ou taxa de falso positivo inválidas.
	ErrParametros = errors.New("bloom: parâmetros inválidos")
	// ErrFormato indica bytes que não formam um filtro válido.
	ErrFormato = errors.New("bloom: dados inválidos")
	// ErrIncompativel indica filtros com tamanhos diferentes numa união.
	ErrIncompativel = errors.New("bloom: filtros incompatíveis")
)

const (
	magic        uint32 = 0x424C4D31 // "BLM1"
	tamCabecalho        = 4 + 4 + 8 + 8
)

// Filtro é um filtro de Bloom seguro para uso concorrente.
type Filtro struct {
	mu   sync.RWMutex
	bits []uint64
	m    uint64 // número de bits
	k    uint32 // número de funções de hash
	n    uint64 // elementos adicionados
}

// Novo dimensiona o filtro para n elementos com taxa de falso positivo p (0<p<1).
func Novo(n int, p float64) (*Filtro, error) {
	if n < 1 || !(p > 0 && p < 1) {
		return nil, ErrParametros
	}
	m := uint64(math.Ceil(-float64(n) * math.Log(p) / (math.Ln2 * math.Ln2)))
	if m < 64 {
		m = 64
	}
	k := uint32(math.Round(float64(m) / float64(n) * math.Ln2))
	if k < 1 {
		k = 1
	}
	return &Filtro{bits: make([]uint64, (m+63)/64), m: m, k: k}, nil
}

func hashes(dado []byte) (h1, h2 uint64) {
	h := uint64(14695981039346656037)
	for _, b := range dado {
		h ^= uint64(b)
		h *= 1099511628211
	}
	h1 = h
	// segundo hash: finalizador do splitmix64 sobre o primeiro
	z := h + 0x9e3779b97f4a7c15
	z = (z ^ (z >> 30)) * 0xbf58476d1ce4e5b9
	z = (z ^ (z >> 27)) * 0x94d049bb133111eb
	h2 = (z ^ (z >> 31)) | 1
	return
}

// Adicionar insere o elemento.
func (f *Filtro) Adicionar(dado []byte) {
	h1, h2 := hashes(dado)
	f.mu.Lock()
	defer f.mu.Unlock()
	for i := uint32(0); i < f.k; i++ {
		pos := (h1 + uint64(i)*h2) % f.m
		f.bits[pos/64] |= 1 << (pos % 64)
	}
	f.n++
}

// Possui devolve false se o elemento certamente não foi adicionado.
func (f *Filtro) Possui(dado []byte) bool {
	h1, h2 := hashes(dado)
	f.mu.RLock()
	defer f.mu.RUnlock()
	for i := uint32(0); i < f.k; i++ {
		pos := (h1 + uint64(i)*h2) % f.m
		if f.bits[pos/64]&(1<<(pos%64)) == 0 {
			return false
		}
	}
	return true
}

// Adicionados devolve quantos elementos foram inseridos (com repetição).
func (f *Filtro) Adicionados() uint64 {
	f.mu.RLock()
	defer f.mu.RUnlock()
	return f.n
}

// Uniao incorpora outro filtro de mesmas dimensões.
func (f *Filtro) Uniao(o *Filtro) error {
	if f == o {
		return nil
	}
	o.mu.RLock()
	defer o.mu.RUnlock()
	f.mu.Lock()
	defer f.mu.Unlock()
	if f.m != o.m || f.k != o.k {
		return ErrIncompativel
	}
	for i := range f.bits {
		f.bits[i] |= o.bits[i]
	}
	f.n += o.n
	return nil
}

// TaxaEstimada estima a taxa atual de falso positivo pela ocupação dos bits.
func (f *Filtro) TaxaEstimada() float64 {
	f.mu.RLock()
	defer f.mu.RUnlock()
	var ligados uint64
	for _, w := range f.bits {
		for ; w != 0; w &= w - 1 {
			ligados++
		}
	}
	return math.Pow(float64(ligados)/float64(f.m), float64(f.k))
}

// MarshalBinary serializa: magic, k, m, n, bits e CRC32 final.
func (f *Filtro) MarshalBinary() ([]byte, error) {
	f.mu.RLock()
	defer f.mu.RUnlock()
	b := make([]byte, tamCabecalho+8*len(f.bits)+4)
	binary.LittleEndian.PutUint32(b[0:], magic)
	binary.LittleEndian.PutUint32(b[4:], f.k)
	binary.LittleEndian.PutUint64(b[8:], f.m)
	binary.LittleEndian.PutUint64(b[16:], f.n)
	for i, w := range f.bits {
		binary.LittleEndian.PutUint64(b[tamCabecalho+8*i:], w)
	}
	fim := len(b) - 4
	binary.LittleEndian.PutUint32(b[fim:], crc32.ChecksumIEEE(b[:fim]))
	return b, nil
}

// Carregar reconstrói um filtro serializado, validando formato e checksum.
func Carregar(b []byte) (*Filtro, error) {
	if len(b) < tamCabecalho+4 || binary.LittleEndian.Uint32(b) != magic {
		return nil, ErrFormato
	}
	fim := len(b) - 4
	if binary.LittleEndian.Uint32(b[fim:]) != crc32.ChecksumIEEE(b[:fim]) {
		return nil, ErrFormato
	}
	k := binary.LittleEndian.Uint32(b[4:])
	m := binary.LittleEndian.Uint64(b[8:])
	n := binary.LittleEndian.Uint64(b[16:])
	if k == 0 || m == 0 || uint64(fim-tamCabecalho) != 8*((m+63)/64) {
		return nil, ErrFormato
	}
	f := &Filtro{bits: make([]uint64, (m+63)/64), m: m, k: k, n: n}
	for i := range f.bits {
		f.bits[i] = binary.LittleEndian.Uint64(b[tamCabecalho+8*i:])
	}
	return f, nil
}
