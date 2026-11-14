// Pacote saude implementa um verificador de saúde (health checker) com
// backoff exponencial para alvos que falham e limiares de queda/recuperação.
// O tempo é passado explicitamente a Executar, sem goroutines nem sleeps,
// o que o torna determinístico e fácil de testar.
package saude

import (
	"sort"
	"sync"
	"time"
)

// Verificador sonda um alvo e devolve nil se ele está saudável.
type Verificador interface {
	Verificar(alvo string) error
}

// VerificadorFunc adapta uma função a Verificador.
type VerificadorFunc func(alvo string) error

// Verificar implementa Verificador.
func (f VerificadorFunc) Verificar(alvo string) error { return f(alvo) }

// Config define a política do verificador.
type Config struct {
	Intervalo      time.Duration // período entre sondas de um alvo saudável
	BackoffMax     time.Duration // teto do intervalo entre sondas de um alvo em falha
	LimiteFalhas   int           // falhas consecutivas para marcar como não saudável (>= 1)
	LimiteSucessos int           // sucessos consecutivos para voltar a saudável (>= 1)
}

// Estado é a situação observada de um alvo.
type Estado struct {
	Alvo      string
	Saudavel  bool
	Falhas    int // falhas consecutivas
	Sucessos  int // sucessos consecutivos
	Proxima   time.Time
	Intervalo time.Duration // intervalo que será usado após a última sonda
}

type alvo struct {
	Estado
}

// Verificadora gerencia vários alvos. É segura para uso concorrente.
type Verificadora struct {
	mu    sync.Mutex
	cfg   Config
	v     Verificador
	alvos map[string]*alvo
}

// Nova cria o verificador. Valores não positivos na config recebem padrões
// (limites 1; BackoffMax = 32 x Intervalo).
func Nova(cfg Config, v Verificador) *Verificadora {
	if cfg.Intervalo <= 0 {
		cfg.Intervalo = time.Second
	}
	if cfg.LimiteFalhas < 1 {
		cfg.LimiteFalhas = 1
	}
	if cfg.LimiteSucessos < 1 {
		cfg.LimiteSucessos = 1
	}
	if cfg.BackoffMax < cfg.Intervalo {
		cfg.BackoffMax = 32 * cfg.Intervalo
	}
	return &Verificadora{cfg: cfg, v: v, alvos: map[string]*alvo{}}
}

// Adicionar passa a monitorar o alvo, inicialmente considerado saudável e
// elegível para sondagem imediata em agora.
func (h *Verificadora) Adicionar(nome string, agora time.Time) {
	h.mu.Lock()
	defer h.mu.Unlock()
	if _, ok := h.alvos[nome]; ok {
		return
	}
	h.alvos[nome] = &alvo{Estado{Alvo: nome, Saudavel: true, Proxima: agora, Intervalo: h.cfg.Intervalo}}
}

// Remover deixa de monitorar o alvo.
func (h *Verificadora) Remover(nome string) {
	h.mu.Lock()
	defer h.mu.Unlock()
	delete(h.alvos, nome)
}

// Executar sonda todos os alvos cuja hora chegou (Proxima <= agora) e agenda a
// próxima sonda de cada um. Em caso de falha o intervalo dobra, até BackoffMax;
// em caso de sucesso volta ao Intervalo base. Devolve os alvos sondados, em
// ordem alfabética.
func (h *Verificadora) Executar(agora time.Time) []string {
	h.mu.Lock()
	defer h.mu.Unlock()
	var devidos []string
	for nome, a := range h.alvos {
		if !a.Proxima.After(agora) {
			devidos = append(devidos, nome)
		}
	}
	sort.Strings(devidos)
	for _, nome := range devidos {
		a := h.alvos[nome]
		if h.v.Verificar(nome) == nil {
			a.Falhas = 0
			a.Sucessos++
			if !a.Saudavel && a.Sucessos >= h.cfg.LimiteSucessos {
				a.Saudavel = true
			}
			a.Intervalo = h.cfg.Intervalo
		} else {
			a.Sucessos = 0
			a.Falhas++
			if a.Saudavel && a.Falhas >= h.cfg.LimiteFalhas {
				a.Saudavel = false
			}
			a.Intervalo = h.backoff(a.Falhas)
		}
		a.Proxima = agora.Add(a.Intervalo)
	}
	return devidos
}

// backoff devolve Intervalo * 2^(falhas-1), limitado a BackoffMax.
func (h *Verificadora) backoff(falhas int) time.Duration {
	d := h.cfg.Intervalo
	for i := 1; i < falhas; i++ {
		d *= 2
		if d >= h.cfg.BackoffMax {
			return h.cfg.BackoffMax
		}
	}
	return min(d, h.cfg.BackoffMax)
}

// Estado devolve a situação atual de um alvo.
func (h *Verificadora) Estado(nome string) (Estado, bool) {
	h.mu.Lock()
	defer h.mu.Unlock()
	a, ok := h.alvos[nome]
	if !ok {
		return Estado{}, false
	}
	return a.Estado, true
}

// Saudaveis devolve, em ordem alfabética, os alvos atualmente saudáveis.
func (h *Verificadora) Saudaveis() []string {
	h.mu.Lock()
	defer h.mu.Unlock()
	var out []string
	for nome, a := range h.alvos {
		if a.Saudavel {
			out = append(out, nome)
		}
	}
	sort.Strings(out)
	return out
}
