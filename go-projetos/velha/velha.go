// Pacote velha implementa o jogo da velha com IA baseada em minimax.
package velha

import (
	"errors"
	"fmt"
)

// Jogadores e célula vazia.
const (
	Vazio byte = ' '
	X     byte = 'X'
	O     byte = 'O'
)

// Erros possíveis.
var (
	ErrPosicaoInvalida = errors.New("velha: posição inválida")
	ErrOcupada         = errors.New("velha: posição ocupada")
)

// Tabuleiro tem 9 casas, indexadas de 0 a 8 em linhas.
type Tabuleiro [9]byte

var linhas = [8][3]int{
	{0, 1, 2}, {3, 4, 5}, {6, 7, 8},
	{0, 3, 6}, {1, 4, 7}, {2, 5, 8},
	{0, 4, 8}, {2, 4, 6},
}

// Novo devolve um tabuleiro vazio.
func Novo() Tabuleiro {
	var t Tabuleiro
	for i := range t {
		t[i] = Vazio
	}
	return t
}

// Jogar coloca a peça do jogador na posição.
func (t *Tabuleiro) Jogar(pos int, j byte) error {
	if pos < 0 || pos > 8 {
		return fmt.Errorf("%w: %d", ErrPosicaoInvalida, pos)
	}
	if t[pos] != Vazio {
		return fmt.Errorf("%w: %d", ErrOcupada, pos)
	}
	t[pos] = j
	return nil
}

// Vencedor devolve X ou O se alguém ganhou, ou Vazio caso contrário.
func (t Tabuleiro) Vencedor() byte {
	for _, l := range linhas {
		if t[l[0]] != Vazio && t[l[0]] == t[l[1]] && t[l[1]] == t[l[2]] {
			return t[l[0]]
		}
	}
	return Vazio
}

// Cheio informa se não há mais casas livres.
func (t Tabuleiro) Cheio() bool {
	for _, c := range t {
		if c == Vazio {
			return false
		}
	}
	return true
}

func oponente(j byte) byte {
	if j == X {
		return O
	}
	return X
}

// minimax devolve a pontuação do tabuleiro do ponto de vista de "eu",
// com "vez" jogando agora. Vitórias mais rápidas valem mais.
func minimax(t Tabuleiro, eu, vez byte, profundidade int) int {
	if v := t.Vencedor(); v != Vazio {
		if v == eu {
			return 10 - profundidade
		}
		return profundidade - 10
	}
	if t.Cheio() {
		return 0
	}
	melhor := -100
	if vez != eu {
		melhor = 100
	}
	for i := range t {
		if t[i] != Vazio {
			continue
		}
		t[i] = vez
		p := minimax(t, eu, oponente(vez), profundidade+1)
		t[i] = Vazio
		if (vez == eu && p > melhor) || (vez != eu && p < melhor) {
			melhor = p
		}
	}
	return melhor
}

// MelhorJogada devolve a melhor posição para o jogador, ou -1 se o jogo acabou.
func (t Tabuleiro) MelhorJogada(j byte) int {
	if t.Vencedor() != Vazio || t.Cheio() {
		return -1
	}
	melhorPos, melhorPont := -1, -100
	for i := range t {
		if t[i] != Vazio {
			continue
		}
		t[i] = j
		p := minimax(t, j, oponente(j), 1)
		t[i] = Vazio
		if p > melhorPont {
			melhorPos, melhorPont = i, p
		}
	}
	return melhorPos
}
