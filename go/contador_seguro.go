package lab

import "sync"

// ContadorSeguro é um contador por chave seguro para uso concorrente.
type ContadorSeguro struct {
	mu      sync.Mutex
	valores map[string]int
}

// NovoContadorSeguro cria um contador vazio.
func NovoContadorSeguro() *ContadorSeguro {
	return &ContadorSeguro{valores: make(map[string]int)}
}

// Incrementar soma delta à chave e devolve o novo valor.
func (c *ContadorSeguro) Incrementar(chave string, delta int) int {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.valores[chave] += delta
	return c.valores[chave]
}

// Valor devolve o valor atual da chave (0 se inexistente).
func (c *ContadorSeguro) Valor(chave string) int {
	c.mu.Lock()
	defer c.mu.Unlock()
	return c.valores[chave]
}

// Total devolve a soma de todas as chaves.
func (c *ContadorSeguro) Total() int {
	c.mu.Lock()
	defer c.mu.Unlock()
	t := 0
	for _, v := range c.valores {
		t += v
	}
	return t
}

// Copia devolve um snapshot dos valores.
func (c *ContadorSeguro) Copia() map[string]int {
	c.mu.Lock()
	defer c.mu.Unlock()
	cp := make(map[string]int, len(c.valores))
	for k, v := range c.valores {
		cp[k] = v
	}
	return cp
}
