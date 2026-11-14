package lab

import (
	"sync"
	"time"
)

// LimitadorTaxa é um token bucket simples. O relógio é injetável para
// permitir testes determinísticos.
type LimitadorTaxa struct {
	mu         sync.Mutex
	capacidade float64
	porSegundo float64
	tokens     float64
	ultimo     time.Time
	agora      func() time.Time
}

// NovoLimitadorTaxa cria um limitador com a capacidade (rajada máxima) e a
// taxa de reposição em tokens por segundo. Se agora for nil, usa time.Now.
// Parâmetros não positivos são ajustados para o mínimo útil.
func NovoLimitadorTaxa(capacidade int, porSegundo float64, agora func() time.Time) *LimitadorTaxa {
	if agora == nil {
		agora = time.Now
	}
	if capacidade < 1 {
		capacidade = 1
	}
	if porSegundo < 0 {
		porSegundo = 0
	}
	return &LimitadorTaxa{
		capacidade: float64(capacidade),
		porSegundo: porSegundo,
		tokens:     float64(capacidade),
		ultimo:     agora(),
		agora:      agora,
	}
}

// Permitir consome um token se houver; devolve false caso contrário.
func (l *LimitadorTaxa) Permitir() bool {
	l.mu.Lock()
	defer l.mu.Unlock()
	t := l.agora()
	if dt := t.Sub(l.ultimo).Seconds(); dt > 0 {
		l.tokens = min(l.capacidade, l.tokens+dt*l.porSegundo)
	}
	l.ultimo = t
	if l.tokens >= 1 {
		l.tokens--
		return true
	}
	return false
}
