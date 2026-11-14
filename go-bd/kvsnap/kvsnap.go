// Pacote kvsnap implementa um armazenamento chave-valor em memória com
// snapshots imutáveis que podem ser consultados ou restaurados depois.
package kvsnap

import (
	"errors"
	"sort"
	"sync"
)

// ErrSnapshotInexistente é retornado quando o id do snapshot não existe.
var ErrSnapshotInexistente = errors.New("kvsnap: snapshot inexistente")

// Loja guarda os dados atuais e os snapshots tirados.
type Loja struct {
	mu      sync.RWMutex
	dados   map[string]string
	snaps   map[int]map[string]string
	proximo int
}

// Nova cria uma loja vazia.
func Nova() *Loja {
	return &Loja{dados: map[string]string{}, snaps: map[int]map[string]string{}, proximo: 1}
}

// Definir grava o valor da chave.
func (l *Loja) Definir(chave, valor string) {
	l.mu.Lock()
	l.dados[chave] = valor
	l.mu.Unlock()
}

// Obter devolve o valor atual da chave.
func (l *Loja) Obter(chave string) (string, bool) {
	l.mu.RLock()
	defer l.mu.RUnlock()
	v, ok := l.dados[chave]
	return v, ok
}

// Remover apaga a chave e informa se ela existia.
func (l *Loja) Remover(chave string) bool {
	l.mu.Lock()
	defer l.mu.Unlock()
	_, ok := l.dados[chave]
	delete(l.dados, chave)
	return ok
}

// Tamanho devolve a quantidade de chaves atuais.
func (l *Loja) Tamanho() int {
	l.mu.RLock()
	defer l.mu.RUnlock()
	return len(l.dados)
}

// Chaves devolve as chaves atuais em ordem.
func (l *Loja) Chaves() []string {
	l.mu.RLock()
	defer l.mu.RUnlock()
	ks := make([]string, 0, len(l.dados))
	for k := range l.dados {
		ks = append(ks, k)
	}
	sort.Strings(ks)
	return ks
}

// Snapshot congela o estado atual e devolve o id para consultas futuras.
func (l *Loja) Snapshot() int {
	l.mu.Lock()
	defer l.mu.Unlock()
	copia := make(map[string]string, len(l.dados))
	for k, v := range l.dados {
		copia[k] = v
	}
	id := l.proximo
	l.proximo++
	l.snaps[id] = copia
	return id
}

// ObterEm lê uma chave dentro de um snapshot.
func (l *Loja) ObterEm(id int, chave string) (string, bool, error) {
	l.mu.RLock()
	defer l.mu.RUnlock()
	s, ok := l.snaps[id]
	if !ok {
		return "", false, ErrSnapshotInexistente
	}
	v, ok := s[chave]
	return v, ok, nil
}

// Restaurar substitui o estado atual pelo conteúdo do snapshot.
func (l *Loja) Restaurar(id int) error {
	l.mu.Lock()
	defer l.mu.Unlock()
	s, ok := l.snaps[id]
	if !ok {
		return ErrSnapshotInexistente
	}
	novo := make(map[string]string, len(s))
	for k, v := range s {
		novo[k] = v
	}
	l.dados = novo
	return nil
}

// Descartar libera um snapshot.
func (l *Loja) Descartar(id int) error {
	l.mu.Lock()
	defer l.mu.Unlock()
	if _, ok := l.snaps[id]; !ok {
		return ErrSnapshotInexistente
	}
	delete(l.snaps, id)
	return nil
}
