// Pacote balanceador implementa três estratégias de balanceamento de carga:
// round robin, menos conexões e hash consistente (anel com nós virtuais).
package balanceador

import (
	"errors"
	"fmt"
	"hash/fnv"
	"sort"
	"sync"
)

// ErrSemBackends indica que não há backend disponível.
var ErrSemBackends = errors.New("balanceador: nenhum backend disponível")

// RoundRobin distribui requisições circularmente.
type RoundRobin struct {
	mu       sync.Mutex
	backends []string
	proximo  int
}

// NovoRoundRobin cria o balanceador com a lista (copiada) de backends.
func NovoRoundRobin(backends ...string) *RoundRobin {
	return &RoundRobin{backends: append([]string(nil), backends...)}
}

// Proximo devolve o próximo backend da rotação.
func (r *RoundRobin) Proximo() (string, error) {
	r.mu.Lock()
	defer r.mu.Unlock()
	if len(r.backends) == 0 {
		return "", ErrSemBackends
	}
	b := r.backends[r.proximo%len(r.backends)]
	r.proximo = (r.proximo + 1) % len(r.backends)
	return b, nil
}

// Remover tira um backend da rotação (ex.: reprovado no health check).
func (r *RoundRobin) Remover(backend string) bool {
	r.mu.Lock()
	defer r.mu.Unlock()
	for i, b := range r.backends {
		if b == backend {
			r.backends = append(r.backends[:i], r.backends[i+1:]...)
			if i < r.proximo {
				r.proximo--
			}
			if len(r.backends) > 0 {
				r.proximo %= len(r.backends)
			} else {
				r.proximo = 0
			}
			return true
		}
	}
	return false
}

// MenosConexoes envia cada requisição ao backend com menos conexões ativas;
// empates são resolvidos pela ordem de cadastro.
type MenosConexoes struct {
	mu       sync.Mutex
	backends []string
	ativas   map[string]int
}

// NovoMenosConexoes cria o balanceador.
func NovoMenosConexoes(backends ...string) *MenosConexoes {
	m := &MenosConexoes{backends: append([]string(nil), backends...), ativas: map[string]int{}}
	return m
}

// Adquirir escolhe o backend menos carregado e registra uma conexão nele.
// O chamador deve chamar Liberar quando a conexão terminar.
func (m *MenosConexoes) Adquirir() (string, error) {
	m.mu.Lock()
	defer m.mu.Unlock()
	if len(m.backends) == 0 {
		return "", ErrSemBackends
	}
	melhor := m.backends[0]
	for _, b := range m.backends[1:] {
		if m.ativas[b] < m.ativas[melhor] {
			melhor = b
		}
	}
	m.ativas[melhor]++
	return melhor, nil
}

// Liberar encerra uma conexão do backend. Devolve erro se ele não tinha conexões.
func (m *MenosConexoes) Liberar(backend string) error {
	m.mu.Lock()
	defer m.mu.Unlock()
	if m.ativas[backend] <= 0 {
		return fmt.Errorf("balanceador: %q sem conexões ativas", backend)
	}
	m.ativas[backend]--
	return nil
}

// Ativas devolve o número de conexões ativas do backend.
func (m *MenosConexoes) Ativas(backend string) int {
	m.mu.Lock()
	defer m.mu.Unlock()
	return m.ativas[backend]
}

// HashConsistente mapeia chaves a backends de modo que adicionar ou remover
// um backend desloque apenas uma fração mínima das chaves.
type HashConsistente struct {
	mu      sync.RWMutex
	nos     int // nós virtuais por backend
	anel    []ponto
	membros map[string]bool
}

type ponto struct {
	hash    uint32
	backend string
}

// NovoHashConsistente cria um anel; nosVirtuais (>= 1) suaviza a distribuição.
func NovoHashConsistente(nosVirtuais int, backends ...string) *HashConsistente {
	if nosVirtuais < 1 {
		nosVirtuais = 1
	}
	h := &HashConsistente{nos: nosVirtuais, membros: map[string]bool{}}
	for _, b := range backends {
		h.Adicionar(b)
	}
	return h
}

func hash32(s string) uint32 {
	f := fnv.New32a()
	f.Write([]byte(s))
	return f.Sum32()
}

// Adicionar insere um backend no anel. Repetir um backend não tem efeito.
func (h *HashConsistente) Adicionar(backend string) {
	h.mu.Lock()
	defer h.mu.Unlock()
	if h.membros[backend] {
		return
	}
	h.membros[backend] = true
	for i := 0; i < h.nos; i++ {
		h.anel = append(h.anel, ponto{hash32(fmt.Sprintf("%s#%d", backend, i)), backend})
	}
	sort.Slice(h.anel, func(i, j int) bool {
		if h.anel[i].hash != h.anel[j].hash {
			return h.anel[i].hash < h.anel[j].hash
		}
		return h.anel[i].backend < h.anel[j].backend
	})
}

// Remover tira um backend do anel.
func (h *HashConsistente) Remover(backend string) bool {
	h.mu.Lock()
	defer h.mu.Unlock()
	if !h.membros[backend] {
		return false
	}
	delete(h.membros, backend)
	novo := h.anel[:0]
	for _, p := range h.anel {
		if p.backend != backend {
			novo = append(novo, p)
		}
	}
	h.anel = novo
	return true
}

// Buscar devolve o backend responsável pela chave: o primeiro nó do anel com
// hash maior ou igual ao da chave, dando a volta se necessário.
func (h *HashConsistente) Buscar(chave string) (string, error) {
	h.mu.RLock()
	defer h.mu.RUnlock()
	if len(h.anel) == 0 {
		return "", ErrSemBackends
	}
	k := hash32(chave)
	i := sort.Search(len(h.anel), func(i int) bool { return h.anel[i].hash >= k })
	if i == len(h.anel) {
		i = 0
	}
	return h.anel[i].backend, nil
}
