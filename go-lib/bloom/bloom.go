// Pacote bloom implementa um filtro de Bloom: conjunto probabilístico que
// nunca dá falso negativo, mas pode dar falso positivo.
package bloom

import (
	"hash/fnv"
	"math"
)

// Filtro é um filtro de Bloom (não seguro para escrita concorrente).
type Filtro struct {
	bits []uint64
	m    uint64 // total de bits
	k    int    // número de funções de hash
	n    int    // itens adicionados
}

// Novo dimensiona o filtro para "esperados" itens com taxa de falso positivo "taxa" (0 < taxa < 1).
func Novo(esperados int, taxa float64) *Filtro {
	if esperados < 1 {
		esperados = 1
	}
	if taxa <= 0 || taxa >= 1 {
		taxa = 0.01
	}
	ln2 := math.Ln2
	m := uint64(math.Ceil(-float64(esperados) * math.Log(taxa) / (ln2 * ln2)))
	m = max(m, 64)
	k := max(1, int(math.Round(float64(m)/float64(esperados)*ln2)))
	return &Filtro{bits: make([]uint64, (m+63)/64), m: m, k: k}
}

// hashes devolve dois hashes base para o esquema de double hashing.
func hashes(dado []byte) (uint64, uint64) {
	h := fnv.New64a()
	h.Write(dado)
	h1 := h.Sum64()
	h.Write([]byte{0xff})
	h2 := h.Sum64() | 1 // ímpar, para varrer bem o espaço de bits
	return h1, h2
}

// Adicionar insere o dado no filtro.
func (f *Filtro) Adicionar(dado []byte) {
	h1, h2 := hashes(dado)
	for i := 0; i < f.k; i++ {
		pos := (h1 + uint64(i)*h2) % f.m
		f.bits[pos/64] |= 1 << (pos % 64)
	}
	f.n++
}

// Talvez informa se o dado possivelmente está no filtro.
// false é definitivo (ausente); true pode ser falso positivo.
func (f *Filtro) Talvez(dado []byte) bool {
	h1, h2 := hashes(dado)
	for i := 0; i < f.k; i++ {
		pos := (h1 + uint64(i)*h2) % f.m
		if f.bits[pos/64]&(1<<(pos%64)) == 0 {
			return false
		}
	}
	return true
}

// AdicionarTexto é um atalho para Adicionar com string.
func (f *Filtro) AdicionarTexto(s string) { f.Adicionar([]byte(s)) }

// TalvezTexto é um atalho para Talvez com string.
func (f *Filtro) TalvezTexto(s string) bool { return f.Talvez([]byte(s)) }

// Adicionados devolve quantas inserções foram feitas.
func (f *Filtro) Adicionados() int { return f.n }

// Parametros devolve o número de bits e de funções de hash.
func (f *Filtro) Parametros() (bits uint64, hashes int) { return f.m, f.k }
