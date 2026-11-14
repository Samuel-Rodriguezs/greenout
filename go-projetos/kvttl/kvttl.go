// Pacote kvttl implementa um key-value store com expiração (TTL)
// e relógio injetável para facilitar testes.
package kvttl

import (
	"sync"
	"time"
)

type entrada struct {
	valor    string
	expiraEm time.Time // zero = nunca expira
}

// Store é um armazenamento chave-valor seguro para uso concorrente.
type Store struct {
	mu    sync.Mutex
	agora func() time.Time
	dados map[string]entrada
}

// Novo cria um Store. Se agora for nil, usa time.Now.
func Novo(agora func() time.Time) *Store {
	if agora == nil {
		agora = time.Now
	}
	return &Store{agora: agora, dados: map[string]entrada{}}
}

// Definir grava a chave; ttl <= 0 significa sem expiração.
func (s *Store) Definir(chave, valor string, ttl time.Duration) {
	s.mu.Lock()
	defer s.mu.Unlock()
	e := entrada{valor: valor}
	if ttl > 0 {
		e.expiraEm = s.agora().Add(ttl)
	}
	s.dados[chave] = e
}

func (e entrada) expirada(agora time.Time) bool {
	return !e.expiraEm.IsZero() && !agora.Before(e.expiraEm)
}

// Obter devolve o valor se a chave existir e não tiver expirado.
func (s *Store) Obter(chave string) (string, bool) {
	s.mu.Lock()
	defer s.mu.Unlock()
	e, ok := s.dados[chave]
	if !ok {
		return "", false
	}
	if e.expirada(s.agora()) {
		delete(s.dados, chave)
		return "", false
	}
	return e.valor, true
}

// Remover apaga a chave e informa se ela existia (e estava válida).
func (s *Store) Remover(chave string) bool {
	_, ok := s.Obter(chave)
	s.mu.Lock()
	delete(s.dados, chave)
	s.mu.Unlock()
	return ok
}

// TTLRestante informa quanto falta para a chave expirar.
// O segundo retorno é false se a chave não existe ou já expirou;
// para chaves sem expiração devolve (0, true).
func (s *Store) TTLRestante(chave string) (time.Duration, bool) {
	s.mu.Lock()
	defer s.mu.Unlock()
	e, ok := s.dados[chave]
	if !ok || e.expirada(s.agora()) {
		return 0, false
	}
	if e.expiraEm.IsZero() {
		return 0, true
	}
	return e.expiraEm.Sub(s.agora()), true
}

// Limpar remove todas as chaves expiradas e devolve quantas foram removidas.
func (s *Store) Limpar() int {
	s.mu.Lock()
	defer s.mu.Unlock()
	agora := s.agora()
	n := 0
	for k, e := range s.dados {
		if e.expirada(agora) {
			delete(s.dados, k)
			n++
		}
	}
	return n
}

// Tamanho devolve o número de entradas armazenadas (inclui expiradas não limpas).
func (s *Store) Tamanho() int {
	s.mu.Lock()
	defer s.mu.Unlock()
	return len(s.dados)
}
