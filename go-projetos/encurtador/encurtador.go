// Pacote encurtador implementa um encurtador de URLs usando base62.
package encurtador

import (
	"errors"
	"fmt"
	"net/url"
	"strings"
	"sync"
)

const alfabeto = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

// Erros possíveis.
var (
	ErrURLInvalida    = errors.New("encurtador: URL inválida")
	ErrCodigoInvalido = errors.New("encurtador: código inválido")
	ErrNaoEncontrado  = errors.New("encurtador: código não encontrado")
)

// Codificar converte um inteiro não negativo para base62.
func Codificar(n uint64) string {
	if n == 0 {
		return string(alfabeto[0])
	}
	var b []byte
	for n > 0 {
		b = append([]byte{alfabeto[n%62]}, b...)
		n /= 62
	}
	return string(b)
}

// Decodificar converte uma string base62 de volta para inteiro.
func Decodificar(s string) (uint64, error) {
	if s == "" {
		return 0, ErrCodigoInvalido
	}
	var n uint64
	for _, c := range s {
		i := strings.IndexRune(alfabeto, c)
		if i < 0 {
			return 0, fmt.Errorf("%w: %q", ErrCodigoInvalido, c)
		}
		n = n*62 + uint64(i)
	}
	return n, nil
}

// Encurtador guarda o mapeamento código -> URL.
type Encurtador struct {
	mu      sync.Mutex
	proximo uint64
	urls    map[uint64]string
	porURL  map[string]string
}

// Novo cria um encurtador vazio. Os IDs começam em 1.
func Novo() *Encurtador {
	return &Encurtador{proximo: 1, urls: map[uint64]string{}, porURL: map[string]string{}}
}

// Encurtar devolve o código da URL; a mesma URL gera sempre o mesmo código.
func (e *Encurtador) Encurtar(original string) (string, error) {
	u, err := url.Parse(original)
	if err != nil || (u.Scheme != "http" && u.Scheme != "https") || u.Host == "" {
		return "", fmt.Errorf("%w: %q", ErrURLInvalida, original)
	}
	e.mu.Lock()
	defer e.mu.Unlock()
	if c, ok := e.porURL[original]; ok {
		return c, nil
	}
	id := e.proximo
	e.proximo++
	codigo := Codificar(id)
	e.urls[id] = original
	e.porURL[original] = codigo
	return codigo, nil
}

// Resolver devolve a URL original de um código.
func (e *Encurtador) Resolver(codigo string) (string, error) {
	id, err := Decodificar(codigo)
	if err != nil {
		return "", err
	}
	e.mu.Lock()
	defer e.mu.Unlock()
	u, ok := e.urls[id]
	if !ok {
		return "", ErrNaoEncontrado
	}
	return u, nil
}
