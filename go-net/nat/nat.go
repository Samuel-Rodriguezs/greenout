// Pacote nat implementa a tabela de um NAT com tradução de portas (PAT /
// NAPT): conexões internas dividem um único IP público, distinguidas pela
// porta externa. Entradas expiram por inatividade, com relógio injetável.
package nat

import (
	"errors"
	"sync"
	"time"

	"greenout/net/ipv4"
)

// Protocolos.
const (
	TCP uint8 = 6
	UDP uint8 = 17
)

// ErrSemPortas indica que o intervalo de portas externas está esgotado.
var ErrSemPortas = errors.New("nat: sem portas externas livres")

// Ponto é um par endereço/porta.
type Ponto struct {
	IP    ipv4.Endereco
	Porta uint16
}

type chaveInterna struct {
	ponto Ponto
	proto uint8
}

type chaveExterna struct {
	porta uint16
	proto uint8
}

type mapeamento struct {
	interno Ponto
	externa uint16
	proto   uint8
	expira  time.Time
}

// Tabela é a tabela de tradução do NAT, segura para uso concorrente.
type Tabela struct {
	mu       sync.Mutex
	publico  ipv4.Endereco
	portaMin uint16
	portaMax uint16
	ttl      time.Duration
	agora    func() time.Time
	proxima  uint16
	saida    map[chaveInterna]*mapeamento
	entrada  map[chaveExterna]*mapeamento
}

// Nova cria um NAT que traduz para o IP publico usando portas de portaMin a
// portaMax (inclusive). Mapeamentos ociosos por ttl são descartados. Se
// relogio for nil usa time.Now.
func Nova(publico ipv4.Endereco, portaMin, portaMax uint16, ttl time.Duration, relogio func() time.Time) (*Tabela, error) {
	if portaMin == 0 || portaMin > portaMax {
		return nil, errors.New("nat: intervalo de portas inválido")
	}
	if relogio == nil {
		relogio = time.Now
	}
	return &Tabela{
		publico: publico, portaMin: portaMin, portaMax: portaMax, ttl: ttl, agora: relogio,
		proxima: portaMin,
		saida:   map[chaveInterna]*mapeamento{},
		entrada: map[chaveExterna]*mapeamento{},
	}, nil
}

// Traduzir trata um pacote de saída de interno: devolve o par (IP público,
// porta externa) a usar como origem. Reaproveita o mapeamento existente (e
// renova seu prazo) ou aloca uma porta livre.
func (t *Tabela) Traduzir(interno Ponto, proto uint8) (Ponto, error) {
	t.mu.Lock()
	defer t.mu.Unlock()
	agora := t.agora()
	t.expirar(agora)
	k := chaveInterna{interno, proto}
	if m, ok := t.saida[k]; ok {
		m.expira = agora.Add(t.ttl)
		return Ponto{t.publico, m.externa}, nil
	}
	total := int(t.portaMax) - int(t.portaMin) + 1
	for i := 0; i < total; i++ {
		porta := t.proxima
		if t.proxima == t.portaMax {
			t.proxima = t.portaMin
		} else {
			t.proxima++
		}
		ke := chaveExterna{porta, proto}
		if _, ocupada := t.entrada[ke]; ocupada {
			continue
		}
		m := &mapeamento{interno: interno, externa: porta, proto: proto, expira: agora.Add(t.ttl)}
		t.saida[k], t.entrada[ke] = m, m
		return Ponto{t.publico, porta}, nil
	}
	return Ponto{}, ErrSemPortas
}

// Reverter trata um pacote de entrada destinado à porta externa: devolve o
// host interno correspondente. Só aceita tráfego de retorno de mapeamentos
// ativos; não renova o prazo (apenas tráfego de saída mantém a entrada viva).
func (t *Tabela) Reverter(portaExterna uint16, proto uint8) (Ponto, bool) {
	t.mu.Lock()
	defer t.mu.Unlock()
	t.expirar(t.agora())
	m, ok := t.entrada[chaveExterna{portaExterna, proto}]
	if !ok {
		return Ponto{}, false
	}
	return m.interno, true
}

// Tamanho devolve o número de mapeamentos ativos.
func (t *Tabela) Tamanho() int {
	t.mu.Lock()
	defer t.mu.Unlock()
	t.expirar(t.agora())
	return len(t.saida)
}

func (t *Tabela) expirar(agora time.Time) {
	for k, m := range t.saida {
		if !agora.Before(m.expira) {
			delete(t.saida, k)
			delete(t.entrada, chaveExterna{m.externa, m.proto})
		}
	}
}
