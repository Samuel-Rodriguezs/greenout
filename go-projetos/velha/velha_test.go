package velha

import (
	"errors"
	"testing"
)

func de(s string) Tabuleiro {
	var t Tabuleiro
	copy(t[:], s)
	return t
}

func TestVencedor(t *testing.T) {
	casos := []struct {
		nome string
		tab  string
		want byte
	}{
		{"vazio", "         ", Vazio},
		{"linha X", "XXX      ", X},
		{"coluna O", "O  O  O  ", O},
		{"diagonal", "X   X   X", X},
		{"anti-diagonal", "  O O O  ", O},
		{"empate", "XOXXOOOXX", Vazio},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := de(c.tab).Vencedor(); got != c.want {
				t.Errorf("got %q, want %q", got, c.want)
			}
		})
	}
}

func TestJogarErros(t *testing.T) {
	tab := Novo()
	if err := tab.Jogar(4, X); err != nil {
		t.Fatal(err)
	}
	if err := tab.Jogar(4, O); !errors.Is(err, ErrOcupada) {
		t.Errorf("erro = %v", err)
	}
	for _, p := range []int{-1, 9} {
		if err := tab.Jogar(p, O); !errors.Is(err, ErrPosicaoInvalida) {
			t.Errorf("pos %d: erro = %v", p, err)
		}
	}
}

func TestMelhorJogada(t *testing.T) {
	casos := []struct {
		nome string
		tab  string
		j    byte
		want int
	}{
		{"vence na hora", "XX OO    ", X, 2},
		{"bloqueia", "XX  O    ", O, 2},
		{"prefere vencer a bloquear", "XX OO    ", O, 5},
		{"jogo acabado", "XXXOO    ", O, -1},
	}
	for _, c := range casos {
		t.Run(c.nome, func(t *testing.T) {
			if got := de(c.tab).MelhorJogada(c.j); got != c.want {
				t.Errorf("got %d, want %d", got, c.want)
			}
		})
	}
}

// Dois jogadores perfeitos sempre empatam.
func TestIAContraIA(t *testing.T) {
	tab := Novo()
	vez := X
	for tab.Vencedor() == Vazio && !tab.Cheio() {
		if err := tab.Jogar(tab.MelhorJogada(vez), vez); err != nil {
			t.Fatal(err)
		}
		vez = oponente(vez)
	}
	if tab.Vencedor() != Vazio {
		t.Errorf("esperava empate, venceu %q", tab.Vencedor())
	}
}

// A IA nunca perde contra qualquer sequência de jogadas do adversário.
func TestIANuncaPerde(t *testing.T) {
	var explorar func(t Tabuleiro, vez byte)
	explorar = func(tab Tabuleiro, vez byte) {
		if tab.Vencedor() == X {
			panic("humano venceu a IA")
		}
		if tab.Vencedor() != Vazio || tab.Cheio() {
			return
		}
		if vez == O { // IA joga O
			tab.Jogar(tab.MelhorJogada(O), O)
			explorar(tab, X)
			return
		}
		for i := range tab {
			if tab[i] == Vazio {
				c := tab
				c[i] = X
				explorar(c, O)
			}
		}
	}
	explorar(Novo(), X)
}
