// Pacote mvcc implementa controle de concorrência multiversão com
// snapshot isolation: cada transação lê o estado confirmado no momento em
// que começou, mais as próprias escritas. No commit vale "first committer
// wins": se outra transação confirmou uma chave que esta também escreveu
// depois do snapshot, o commit falha com ErrConflito.
//
// Snapshot isolation não é serializável: anomalias como write skew (duas
// transações leem chaves diferentes e escrevem em chaves diferentes com base
// no que leram) continuam possíveis.
package mvcc

import (
	"errors"
	"sort"
	"sync"
)

var (
	// ErrConflito indica conflito de escrita com uma transação já confirmada.
	ErrConflito = errors.New("mvcc: conflito de escrita")
	// ErrFinalizada indica uso de uma transação já confirmada ou abortada.
	ErrFinalizada = errors.New("mvcc: transação finalizada")
)

type versao struct {
	ts      uint64
	valor   []byte
	apagado bool
}

type escrita struct {
	valor   []byte
	apagado bool
}

// Banco guarda as versões de cada chave em ordem crescente de timestamp.
type Banco struct {
	mu     sync.RWMutex
	dados  map[string][]versao
	ts     uint64 // timestamp do último commit
	ativas map[*Tx]struct{}
}

// Novo cria um banco vazio.
func Novo() *Banco {
	return &Banco{dados: map[string][]versao{}, ativas: map[*Tx]struct{}{}}
}

// Tx é uma transação com snapshot fixo.
type Tx struct {
	b        *Banco
	snap     uint64
	escritas map[string]escrita
	fim      bool
}

// Comecar inicia uma transação enxergando tudo que já foi confirmado.
func (b *Banco) Comecar() *Tx {
	b.mu.Lock()
	defer b.mu.Unlock()
	tx := &Tx{b: b, snap: b.ts, escritas: map[string]escrita{}}
	b.ativas[tx] = struct{}{}
	return tx
}

// Snapshot devolve o timestamp lido por esta transação.
func (tx *Tx) Snapshot() uint64 { return tx.snap }

// visivel devolve a versão mais recente com ts <= snap.
func visivel(vs []versao, snap uint64) (versao, bool) {
	i := sort.Search(len(vs), func(i int) bool { return vs[i].ts > snap })
	if i == 0 {
		return versao{}, false
	}
	return vs[i-1], true
}

// Obter lê a chave: primeiro as escritas da própria transação, depois o snapshot.
func (tx *Tx) Obter(chave string) ([]byte, bool, error) {
	if tx.fim {
		return nil, false, ErrFinalizada
	}
	if w, ok := tx.escritas[chave]; ok {
		if w.apagado {
			return nil, false, nil
		}
		return append([]byte{}, w.valor...), true, nil
	}
	tx.b.mu.RLock()
	defer tx.b.mu.RUnlock()
	v, ok := visivel(tx.b.dados[chave], tx.snap)
	if !ok || v.apagado {
		return nil, false, nil
	}
	return append([]byte{}, v.valor...), true, nil
}

// Definir registra uma escrita local, visível aos outros só após o commit.
func (tx *Tx) Definir(chave string, valor []byte) error {
	if tx.fim {
		return ErrFinalizada
	}
	tx.escritas[chave] = escrita{valor: append([]byte{}, valor...)}
	return nil
}

// Remover registra uma remoção local.
func (tx *Tx) Remover(chave string) error {
	if tx.fim {
		return ErrFinalizada
	}
	tx.escritas[chave] = escrita{apagado: true}
	return nil
}

// Commit confirma as escritas atomicamente, ou falha com ErrConflito e
// descarta a transação.
func (tx *Tx) Commit() error {
	if tx.fim {
		return ErrFinalizada
	}
	b := tx.b
	b.mu.Lock()
	defer b.mu.Unlock()
	tx.fim = true
	delete(b.ativas, tx)
	for k := range tx.escritas {
		if vs := b.dados[k]; len(vs) > 0 && vs[len(vs)-1].ts > tx.snap {
			return ErrConflito
		}
	}
	if len(tx.escritas) == 0 {
		return nil
	}
	b.ts++
	for k, w := range tx.escritas {
		b.dados[k] = append(b.dados[k], versao{ts: b.ts, valor: w.valor, apagado: w.apagado})
	}
	return nil
}

// Abortar descarta a transação. Chamar depois de finalizada é inofensivo.
func (tx *Tx) Abortar() {
	if tx.fim {
		return
	}
	tx.b.mu.Lock()
	defer tx.b.mu.Unlock()
	tx.fim = true
	delete(tx.b.ativas, tx)
}

// Podar descarta versões que nenhuma transação ativa (nem futura) pode mais
// enxergar e devolve quantas foram removidas.
func (b *Banco) Podar() int {
	b.mu.Lock()
	defer b.mu.Unlock()
	minimo := b.ts
	for tx := range b.ativas {
		if tx.snap < minimo {
			minimo = tx.snap
		}
	}
	removidas := 0
	for k, vs := range b.dados {
		// a versão visível no snapshot mínimo é a mais antiga que ainda importa
		i := sort.Search(len(vs), func(i int) bool { return vs[i].ts > minimo }) - 1
		if i < 0 {
			continue
		}
		if i > 0 {
			removidas += i
			vs = append([]versao(nil), vs[i:]...)
		}
		if len(vs) == 1 && vs[0].apagado {
			removidas++
			delete(b.dados, k)
			continue
		}
		b.dados[k] = vs
	}
	return removidas
}

// NumVersoes devolve o total de versões armazenadas (para diagnóstico).
func (b *Banco) NumVersoes() int {
	b.mu.RLock()
	defer b.mu.RUnlock()
	n := 0
	for _, vs := range b.dados {
		n += len(vs)
	}
	return n
}
