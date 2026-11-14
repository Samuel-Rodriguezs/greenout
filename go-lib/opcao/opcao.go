// Pacote opcao fornece os tipos Opcao (valor opcional) e Resultado (valor ou erro).
package opcao

import "errors"

// Opcao representa um valor que pode estar ausente.
type Opcao[T any] struct {
	v   T
	tem bool
}

// Algum cria uma Opcao com valor.
func Algum[T any](v T) Opcao[T] { return Opcao[T]{v: v, tem: true} }

// Nenhum cria uma Opcao vazia.
func Nenhum[T any]() Opcao[T] { return Opcao[T]{} }

// TemValor informa se há valor.
func (o Opcao[T]) TemValor() bool { return o.tem }

// Valor devolve o valor e se ele existe.
func (o Opcao[T]) Valor() (T, bool) { return o.v, o.tem }

// ValorOu devolve o valor ou o padrão informado.
func (o Opcao[T]) ValorOu(padrao T) T {
	if o.tem {
		return o.v
	}
	return padrao
}

// MapearOpcao aplica f quando há valor.
func MapearOpcao[T, R any](o Opcao[T], f func(T) R) Opcao[R] {
	if !o.tem {
		return Nenhum[R]()
	}
	return Algum(f(o.v))
}

// Resultado representa sucesso (valor) ou falha (erro).
type Resultado[T any] struct {
	v   T
	err error
}

// Ok cria um Resultado de sucesso.
func Ok[T any](v T) Resultado[T] { return Resultado[T]{v: v} }

// Falha cria um Resultado de erro. Um erro nil é convertido em erro genérico.
func Falha[T any](err error) Resultado[T] {
	if err == nil {
		err = errors.New("opcao: falha sem erro")
	}
	return Resultado[T]{err: err}
}

// De converte o par (valor, erro) em Resultado.
func De[T any](v T, err error) Resultado[T] {
	if err != nil {
		return Falha[T](err)
	}
	return Ok(v)
}

// EhOk informa se é sucesso.
func (r Resultado[T]) EhOk() bool { return r.err == nil }

// Desempacotar devolve o par (valor, erro).
func (r Resultado[T]) Desempacotar() (T, error) { return r.v, r.err }

// ValorOu devolve o valor em caso de sucesso, ou o padrão.
func (r Resultado[T]) ValorOu(padrao T) T {
	if r.err != nil {
		return padrao
	}
	return r.v
}

// MapearResultado aplica f em caso de sucesso, propagando o erro caso contrário.
func MapearResultado[T, R any](r Resultado[T], f func(T) R) Resultado[R] {
	if r.err != nil {
		return Falha[R](r.err)
	}
	return Ok(f(r.v))
}

// EncadearResultado aplica f (que pode falhar) em caso de sucesso.
func EncadearResultado[T, R any](r Resultado[T], f func(T) Resultado[R]) Resultado[R] {
	if r.err != nil {
		return Falha[R](r.err)
	}
	return f(r.v)
}
