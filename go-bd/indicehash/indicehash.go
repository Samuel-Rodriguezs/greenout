// Pacote indicehash implementa um índice hash em memória (chave de texto
// para uma lista de RIDs) com encadeamento por bucket e crescimento
// automático por duplicação quando o fator de carga passa de 0,75.
package indicehash

import "sync"

const (
	capacidadeInicial = 8
	fatorCarga        = 0.75
)

type entrada struct {
	chave string
	rids  []uint64
	prox  *entrada
}

// Indice mapeia chaves para múltiplos RIDs (índice não único).
type Indice struct {
	mu     sync.RWMutex
	baldes []*entrada
	chaves int // chaves distintas
	pares  int // pares (chave, rid)
}

// Novo cria um índice vazio.
func Novo() *Indice {
	return &Indice{baldes: make([]*entrada, capacidadeInicial)}
}

// hash é o FNV-1a de 64 bits.
func hash(s string) uint64 {
	h := uint64(14695981039346656037)
	for i := 0; i < len(s); i++ {
		h ^= uint64(s[i])
		h *= 1099511628211
	}
	return h
}

func (x *Indice) achar(chave string) *entrada {
	for e := x.baldes[hash(chave)%uint64(len(x.baldes))]; e != nil; e = e.prox {
		if e.chave == chave {
			return e
		}
	}
	return nil
}

func (x *Indice) crescer() {
	novos := make([]*entrada, len(x.baldes)*2)
	for _, e := range x.baldes {
		for e != nil {
			prox := e.prox
			i := hash(e.chave) % uint64(len(novos))
			e.prox = novos[i]
			novos[i] = e
			e = prox
		}
	}
	x.baldes = novos
}

// Inserir associa o rid à chave. Devolve false se o par já existia.
func (x *Indice) Inserir(chave string, rid uint64) bool {
	x.mu.Lock()
	defer x.mu.Unlock()
	if e := x.achar(chave); e != nil {
		for _, r := range e.rids {
			if r == rid {
				return false
			}
		}
		e.rids = append(e.rids, rid)
		x.pares++
		return true
	}
	if float64(x.chaves+1) > fatorCarga*float64(len(x.baldes)) {
		x.crescer()
	}
	i := hash(chave) % uint64(len(x.baldes))
	x.baldes[i] = &entrada{chave: chave, rids: []uint64{rid}, prox: x.baldes[i]}
	x.chaves++
	x.pares++
	return true
}

// Buscar devolve uma cópia dos RIDs da chave, na ordem de inserção.
func (x *Indice) Buscar(chave string) []uint64 {
	x.mu.RLock()
	defer x.mu.RUnlock()
	if e := x.achar(chave); e != nil {
		return append([]uint64(nil), e.rids...)
	}
	return nil
}

// Remover desfaz um par (chave, rid); devolve true se existia.
func (x *Indice) Remover(chave string, rid uint64) bool {
	x.mu.Lock()
	defer x.mu.Unlock()
	e := x.achar(chave)
	if e == nil {
		return false
	}
	for i, r := range e.rids {
		if r != rid {
			continue
		}
		e.rids = append(e.rids[:i], e.rids[i+1:]...)
		x.pares--
		if len(e.rids) == 0 {
			x.desligar(chave)
		}
		return true
	}
	return false
}

// RemoverChave apaga a chave inteira e devolve quantos RIDs tinha.
func (x *Indice) RemoverChave(chave string) int {
	x.mu.Lock()
	defer x.mu.Unlock()
	e := x.achar(chave)
	if e == nil {
		return 0
	}
	n := len(e.rids)
	x.pares -= n
	x.desligar(chave)
	return n
}

// desligar tira a entrada da lista do bucket. x.mu deve estar travado.
func (x *Indice) desligar(chave string) {
	i := hash(chave) % uint64(len(x.baldes))
	var ant *entrada
	for e := x.baldes[i]; e != nil; ant, e = e, e.prox {
		if e.chave != chave {
			continue
		}
		if ant == nil {
			x.baldes[i] = e.prox
		} else {
			ant.prox = e.prox
		}
		x.chaves--
		return
	}
}

// NumChaves devolve a quantidade de chaves distintas.
func (x *Indice) NumChaves() int {
	x.mu.RLock()
	defer x.mu.RUnlock()
	return x.chaves
}

// NumPares devolve a quantidade de pares (chave, rid).
func (x *Indice) NumPares() int {
	x.mu.RLock()
	defer x.mu.RUnlock()
	return x.pares
}
