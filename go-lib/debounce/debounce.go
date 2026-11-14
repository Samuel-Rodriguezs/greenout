// Pacote debounce oferece Debounce e Throttle baseados em consulta (polling)
// com relógio injetável, o que os torna totalmente determinísticos em testes.
package debounce

import (
	"sync"
	"time"
)

// Debounce dispara apenas depois que passou "espera" sem novos eventos.
type Debounce struct {
	mu       sync.Mutex
	espera   time.Duration
	agora    func() time.Time
	ultimo   time.Time
	pendente bool
}

// NovoDebounce cria um Debounce. Se agora for nil, usa time.Now.
func NovoDebounce(espera time.Duration, agora func() time.Time) *Debounce {
	if agora == nil {
		agora = time.Now
	}
	return &Debounce{espera: espera, agora: agora}
}

// Registrar anota a ocorrência de um evento e reinicia a contagem.
func (d *Debounce) Registrar() {
	d.mu.Lock()
	defer d.mu.Unlock()
	d.ultimo = d.agora()
	d.pendente = true
}

// Pronto devolve true (uma única vez por rajada) quando há evento pendente e
// o silêncio já durou ao menos "espera".
func (d *Debounce) Pronto() bool {
	d.mu.Lock()
	defer d.mu.Unlock()
	if !d.pendente || d.agora().Sub(d.ultimo) < d.espera {
		return false
	}
	d.pendente = false
	return true
}

// Throttle permite no máximo uma execução por intervalo.
type Throttle struct {
	mu        sync.Mutex
	intervalo time.Duration
	agora     func() time.Time
	ultimo    time.Time
	usado     bool
}

// NovoThrottle cria um Throttle. Se agora for nil, usa time.Now.
func NovoThrottle(intervalo time.Duration, agora func() time.Time) *Throttle {
	if agora == nil {
		agora = time.Now
	}
	return &Throttle{intervalo: intervalo, agora: agora}
}

// Permitir devolve true se já passou o intervalo desde a última permissão concedida.
func (t *Throttle) Permitir() bool {
	t.mu.Lock()
	defer t.mu.Unlock()
	agora := t.agora()
	if t.usado && agora.Sub(t.ultimo) < t.intervalo {
		return false
	}
	t.usado = true
	t.ultimo = agora
	return true
}
