// Pacote semaforo implementa um semáforo contador usando channels.
package semaforo

import "context"

// Semaforo limita o número de detentores simultâneos.
type Semaforo struct {
	vagas chan struct{}
}

// Novo cria um semáforo com n vagas (mínimo 1).
func Novo(n int) *Semaforo {
	return &Semaforo{vagas: make(chan struct{}, max(1, n))}
}

// Adquirir bloqueia até obter uma vaga ou até o contexto terminar.
func (s *Semaforo) Adquirir(ctx context.Context) error {
	// verifica o contexto primeiro para que um ctx já cancelado nunca adquira
	if err := ctx.Err(); err != nil {
		return err
	}
	select {
	case s.vagas <- struct{}{}:
		return nil
	case <-ctx.Done():
		return ctx.Err()
	}
}

// TentarAdquirir obtém uma vaga sem bloquear.
func (s *Semaforo) TentarAdquirir() bool {
	select {
	case s.vagas <- struct{}{}:
		return true
	default:
		return false
	}
}

// Liberar devolve uma vaga. Liberar sem ter adquirido causa panic.
func (s *Semaforo) Liberar() {
	select {
	case <-s.vagas:
	default:
		panic("semaforo: Liberar sem Adquirir")
	}
}

// EmUso devolve quantas vagas estão ocupadas.
func (s *Semaforo) EmUso() int { return len(s.vagas) }

// Capacidade devolve o total de vagas.
func (s *Semaforo) Capacidade() int { return cap(s.vagas) }
