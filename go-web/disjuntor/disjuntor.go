// Pacote disjuntor implementa um circuit breaker como http.RoundTripper, com
// relógio injetável.
package disjuntor

import (
	"errors"
	"net/http"
	"sync"
	"time"
)

// Estado do disjuntor.
type Estado int

const (
	Fechado Estado = iota
	Aberto
	MeioAberto
)

func (e Estado) String() string {
	return [...]string{"fechado", "aberto", "meio-aberto"}[e]
}

// ErrAberto é retornado enquanto o circuito está aberto.
var ErrAberto = errors.New("disjuntor aberto")

// Disjuntor abre após Limite falhas consecutivas e tenta de novo após Espera.
type Disjuntor struct {
	Base   http.RoundTripper
	Limite int
	Espera time.Duration
	Agora  func() time.Time

	mu         sync.Mutex
	estado     Estado
	falhas     int
	abertoEm   time.Time
	sondaAtiva bool
}

// Novo cria um disjuntor. agora nulo usa time.Now; base nulo usa DefaultTransport.
func Novo(base http.RoundTripper, limite int, espera time.Duration, agora func() time.Time) *Disjuntor {
	if base == nil {
		base = http.DefaultTransport
	}
	if agora == nil {
		agora = time.Now
	}
	return &Disjuntor{Base: base, Limite: limite, Espera: espera, Agora: agora}
}

// Estado retorna o estado atual (considerando a expiração da espera).
func (d *Disjuntor) Estado() Estado {
	d.mu.Lock()
	defer d.mu.Unlock()
	if d.estado == Aberto && d.Agora().Sub(d.abertoEm) >= d.Espera {
		return MeioAberto
	}
	return d.estado
}

func (d *Disjuntor) antes() error {
	d.mu.Lock()
	defer d.mu.Unlock()
	switch d.estado {
	case Aberto:
		if d.Agora().Sub(d.abertoEm) < d.Espera {
			return ErrAberto
		}
		d.estado = MeioAberto
		d.sondaAtiva = true
	case MeioAberto:
		if d.sondaAtiva {
			return ErrAberto // só uma requisição de teste por vez
		}
		d.sondaAtiva = true
	}
	return nil
}

func (d *Disjuntor) depois(falhou bool) {
	d.mu.Lock()
	defer d.mu.Unlock()
	d.sondaAtiva = false
	if !falhou {
		d.estado, d.falhas = Fechado, 0
		return
	}
	d.falhas++
	if d.estado == MeioAberto || d.falhas >= d.Limite {
		d.estado = Aberto
		d.abertoEm = d.Agora()
	}
}

// RoundTrip implementa http.RoundTripper. Erros de rede e respostas 5xx contam como falha.
func (d *Disjuntor) RoundTrip(req *http.Request) (*http.Response, error) {
	if err := d.antes(); err != nil {
		return nil, err
	}
	resp, err := d.Base.RoundTrip(req)
	d.depois(err != nil || resp.StatusCode >= 500)
	return resp, err
}
