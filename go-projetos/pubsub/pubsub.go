// Pacote pubsub implementa um barramento de mensagens publicar/assinar
// por tópicos, usando channels.
package pubsub

import (
	"errors"
	"sync"
)

// ErrFechado indica que o barramento já foi encerrado.
var ErrFechado = errors.New("pubsub: barramento fechado")

// Barramento distribui mensagens aos assinantes de cada tópico.
type Barramento struct {
	mu          sync.RWMutex
	assinantes  map[string][]chan string
	fechado     bool
	tamanhoFila int
}

// Novo cria um barramento; cada assinante recebe uma fila de tamanhoFila.
func Novo(tamanhoFila int) *Barramento {
	return &Barramento{assinantes: map[string][]chan string{}, tamanhoFila: tamanhoFila}
}

// Assinar devolve um channel que recebe as mensagens do tópico.
func (b *Barramento) Assinar(topico string) (<-chan string, error) {
	b.mu.Lock()
	defer b.mu.Unlock()
	if b.fechado {
		return nil, ErrFechado
	}
	ch := make(chan string, b.tamanhoFila)
	b.assinantes[topico] = append(b.assinantes[topico], ch)
	return ch, nil
}

// Publicar envia a mensagem a todos os assinantes do tópico sem bloquear:
// se a fila de um assinante estiver cheia, a mensagem é descartada para ele.
// Devolve o número de assinantes que receberam a mensagem.
func (b *Barramento) Publicar(topico, msg string) (int, error) {
	b.mu.RLock()
	defer b.mu.RUnlock()
	if b.fechado {
		return 0, ErrFechado
	}
	entregues := 0
	for _, ch := range b.assinantes[topico] {
		select {
		case ch <- msg:
			entregues++
		default:
		}
	}
	return entregues, nil
}

// Cancelar remove a assinatura e fecha o channel.
func (b *Barramento) Cancelar(topico string, ch <-chan string) {
	b.mu.Lock()
	defer b.mu.Unlock()
	lista := b.assinantes[topico]
	for i, c := range lista {
		if (<-chan string)(c) == ch {
			b.assinantes[topico] = append(lista[:i], lista[i+1:]...)
			close(c)
			return
		}
	}
}

// Fechar encerra o barramento e fecha todos os channels. É idempotente.
func (b *Barramento) Fechar() {
	b.mu.Lock()
	defer b.mu.Unlock()
	if b.fechado {
		return
	}
	b.fechado = true
	for _, lista := range b.assinantes {
		for _, c := range lista {
			close(c)
		}
	}
	b.assinantes = nil
}
