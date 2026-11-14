// Pacote desligamento executa um servidor e o encerra de forma graciosa quando
// o contexto é cancelado.
package desligamento

import (
	"context"
	"errors"
	"net/http"
	"time"
)

// Servidor é o subconjunto de *http.Server usado aqui (facilita testes).
type Servidor interface {
	ListenAndServe() error
	Shutdown(ctx context.Context) error
}

// Executar inicia o servidor e bloqueia até ele terminar. Quando ctx é
// cancelado, chama Shutdown com o prazo informado. Retorna nil em um
// encerramento limpo.
func Executar(ctx context.Context, srv Servidor, prazo time.Duration) error {
	erroServ := make(chan error, 1)
	go func() { erroServ <- srv.ListenAndServe() }()

	select {
	case err := <-erroServ:
		// O servidor terminou sozinho (ex.: porta ocupada).
		if errors.Is(err, http.ErrServerClosed) {
			return nil
		}
		return err
	case <-ctx.Done():
	}

	sctx, cancel := context.WithTimeout(context.WithoutCancel(ctx), prazo)
	defer cancel()
	if err := srv.Shutdown(sctx); err != nil {
		return err
	}
	if err := <-erroServ; err != nil && !errors.Is(err, http.ErrServerClosed) {
		return err
	}
	return nil
}
