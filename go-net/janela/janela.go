// Pacote janela simula protocolos de janela deslizante (Go-Back-N e
// Selective Repeat) sobre um canal com perdas determinísticas.
//
// O modelo é por rodadas, em que cada rodada equivale a um RTT: o remetente
// transmite sua janela, o receptor responde com ACKs e, ao final da rodada,
// tudo o que não foi confirmado é considerado perdido (timeout).
package janela

import (
	"errors"
	"math/rand"
)

// Erros de simulação.
var (
	ErrParametros   = errors.New("janela: parâmetros inválidos")
	ErrSemProgresso = errors.New("janela: limite de rodadas excedido sem concluir")
)

const maxRodadas = 100000

// Canal decide, de forma reproduzível, quais transmissões são perdidas.
type Canal struct {
	rng      *rand.Rand
	perdaPct int
	Enviados int
	Perdidos int
}

// NovoCanal cria um canal com semente fixa e perda em porcentagem (0 a 100).
func NovoCanal(seed int64, perdaPct int) *Canal {
	return &Canal{rng: rand.New(rand.NewSource(seed)), perdaPct: perdaPct}
}

// Entrega registra uma transmissão e informa se ela chegou ao destino.
func (c *Canal) Entrega() bool {
	c.Enviados++
	if c.rng.Intn(100) < c.perdaPct {
		c.Perdidos++
		return false
	}
	return true
}

// Resultado resume uma simulação.
type Resultado struct {
	Entregues    []int // sequências entregues à aplicação, na ordem de entrega
	Transmissoes int   // pacotes de dados enviados (inclui retransmissões)
	Rodadas      int
}

func valida(total, janela int, c *Canal) error {
	if total < 0 || janela < 1 || c == nil || c.perdaPct < 0 || c.perdaPct > 100 {
		return ErrParametros
	}
	return nil
}

// GoBackN transmite total pacotes numerados de 0 a total-1 com janela do
// remetente de tamanho janela e receptor de janela 1 (descarta fora de ordem,
// ACK cumulativo). Ao expirar, o remetente retransmite desde a base.
func GoBackN(total, janela int, c *Canal) (Resultado, error) {
	if err := valida(total, janela, c); err != nil {
		return Resultado{}, err
	}
	var r Resultado
	base, esperado := 0, 0
	for base < total {
		if r.Rodadas++; r.Rodadas > maxRodadas {
			return r, ErrSemProgresso
		}
		fim := min(base+janela, total)
		ackMax := base
		for seq := base; seq < fim; seq++ {
			r.Transmissoes++
			if !c.Entrega() {
				continue
			}
			if seq == esperado {
				r.Entregues = append(r.Entregues, seq)
				esperado++
			}
			// ACK cumulativo: próximo número esperado.
			if c.Entrega() && esperado > ackMax {
				ackMax = esperado
			}
		}
		base = ackMax
	}
	return r, nil
}

// SelectiveRepeat é como GoBackN, mas o receptor armazena pacotes fora de
// ordem dentro da janela e confirma cada um individualmente; o remetente
// retransmite apenas os pacotes não confirmados.
func SelectiveRepeat(total, janela int, c *Canal) (Resultado, error) {
	if err := valida(total, janela, c); err != nil {
		return Resultado{}, err
	}
	var r Resultado
	confirmado := make([]bool, total) // visão do remetente
	recebido := make([]bool, total)   // buffer do receptor
	base, esperado := 0, 0
	for base < total {
		if r.Rodadas++; r.Rodadas > maxRodadas {
			return r, ErrSemProgresso
		}
		fim := min(base+janela, total)
		for seq := base; seq < fim; seq++ {
			if confirmado[seq] {
				continue
			}
			r.Transmissoes++
			if !c.Entrega() {
				continue
			}
			recebido[seq] = true
			for esperado < total && recebido[esperado] {
				r.Entregues = append(r.Entregues, esperado)
				esperado++
			}
			if c.Entrega() {
				confirmado[seq] = true
			}
		}
		for base < total && confirmado[base] {
			base++
		}
	}
	return r, nil
}
