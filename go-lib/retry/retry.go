// Pacote retry executa uma operação com novas tentativas e backoff exponencial.
// A função de espera é injetável para permitir testes sem dormir de verdade.
package retry

import (
	"errors"
	"fmt"
	"time"
)

// Config define o comportamento das tentativas.
type Config struct {
	Tentativas int                 // total de execuções (mínimo 1)
	Base       time.Duration       // espera antes da 2ª tentativa
	Fator      float64             // multiplicador a cada falha (padrão 2)
	Maximo     time.Duration       // teto da espera (0 = sem teto)
	Dormir     func(time.Duration) // padrão: time.Sleep
}

// ErroPermanente embrulha um erro que não deve ser repetido.
type ErroPermanente struct{ Err error }

func (e *ErroPermanente) Error() string { return e.Err.Error() }
func (e *ErroPermanente) Unwrap() error { return e.Err }

// Permanente marca err como não repetível.
func Permanente(err error) error { return &ErroPermanente{Err: err} }

// ErroEsgotado é devolvido quando todas as tentativas falham.
type ErroEsgotado struct {
	Tentativas int
	Ultimo     error
}

func (e *ErroEsgotado) Error() string {
	return fmt.Sprintf("retry: %d tentativas esgotadas: %v", e.Tentativas, e.Ultimo)
}
func (e *ErroEsgotado) Unwrap() error { return e.Ultimo }

// Espera calcula o tempo de espera após a falha de número n (1 = primeira falha).
func (c Config) Espera(n int) time.Duration {
	fator := c.Fator
	if fator < 1 {
		fator = 2
	}
	d := float64(c.Base)
	for i := 1; i < n; i++ {
		d *= fator
		if c.Maximo > 0 && d >= float64(c.Maximo) {
			return c.Maximo
		}
	}
	if c.Maximo > 0 && time.Duration(d) > c.Maximo {
		return c.Maximo
	}
	return time.Duration(d)
}

// Executar roda f até ter sucesso, esgotar as tentativas ou receber um erro permanente.
func Executar(c Config, f func(tentativa int) error) error {
	total := max(1, c.Tentativas)
	dormir := c.Dormir
	if dormir == nil {
		dormir = time.Sleep
	}
	var err error
	for i := 1; i <= total; i++ {
		err = f(i)
		if err == nil {
			return nil
		}
		var perm *ErroPermanente
		if errors.As(err, &perm) {
			return perm.Err
		}
		if i < total {
			dormir(c.Espera(i))
		}
	}
	return &ErroEsgotado{Tentativas: total, Ultimo: err}
}
