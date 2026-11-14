// Pacote grupo implementa uma versão simplificada de errgroup:
// executa tarefas concorrentes e devolve o primeiro erro.
package grupo

import (
	"context"
	"sync"
)

// Grupo coordena um conjunto de goroutines.
type Grupo struct {
	wg      sync.WaitGroup
	once    sync.Once
	err     error
	cancela context.CancelFunc
	limite  chan struct{}
}

// Novo cria um grupo sem contexto.
func Novo() *Grupo { return &Grupo{} }

// ComContexto cria um grupo e um contexto derivado que é cancelado
// no primeiro erro ou quando Esperar retorna.
func ComContexto(ctx context.Context) (*Grupo, context.Context) {
	ctx, cancela := context.WithCancel(ctx)
	return &Grupo{cancela: cancela}, ctx
}

// Limitar define o máximo de tarefas simultâneas (n <= 0 remove o limite).
// Deve ser chamado antes de Go.
func (g *Grupo) Limitar(n int) {
	if n <= 0 {
		g.limite = nil
		return
	}
	g.limite = make(chan struct{}, n)
}

// Go inicia f em uma nova goroutine. Se houver limite, bloqueia até haver vaga.
func (g *Grupo) Go(f func() error) {
	if g.limite != nil {
		g.limite <- struct{}{}
	}
	g.wg.Add(1)
	go func() {
		defer func() {
			if g.limite != nil {
				<-g.limite
			}
			g.wg.Done()
		}()
		if err := f(); err != nil {
			g.once.Do(func() {
				g.err = err
				if g.cancela != nil {
					g.cancela()
				}
			})
		}
	}()
}

// Esperar aguarda todas as tarefas e devolve o primeiro erro ocorrido.
func (g *Grupo) Esperar() error {
	g.wg.Wait()
	if g.cancela != nil {
		g.cancela()
	}
	return g.err
}
