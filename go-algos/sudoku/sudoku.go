// Pacote sudoku resolve sudokus 9x9 por backtracking com bitmasks e a
// heurística de menor número de candidatos.
package sudoku

import "math/bits"

// Grade é um tabuleiro 9x9; 0 representa célula vazia.
type Grade [9][9]int

// Ler converte nove linhas de texto ('1'-'9' ou '.'/'0' para vazio) em Grade.
// Devolve ok=false se o formato estiver errado.
func Ler(linhas [9]string) (Grade, bool) {
	var g Grade
	for l, s := range linhas {
		if len(s) != 9 {
			return g, false
		}
		for c := 0; c < 9; c++ {
			switch ch := s[c]; {
			case ch == '.' || ch == '0':
			case ch >= '1' && ch <= '9':
				g[l][c] = int(ch - '0')
			default:
				return g, false
			}
		}
	}
	return g, true
}

type estado struct {
	linha, coluna, caixa [9]int // máscaras de dígitos usados (bit d)
}

func caixaDe(l, c int) int { return (l/3)*3 + c/3 }

// alterna liga/desliga o dígito d nas máscaras da linha, coluna e caixa.
func (e *estado) alterna(l, c, d int) {
	bit := 1 << d
	e.linha[l] ^= bit
	e.coluna[c] ^= bit
	e.caixa[caixaDe(l, c)] ^= bit
}

// Resolver preenche g em lugar. Devolve false se a grade for inconsistente
// ou não tiver solução (g fica inalterada nesse caso).
func Resolver(g *Grade) bool {
	var e estado
	for l := 0; l < 9; l++ {
		for c := 0; c < 9; c++ {
			d := g[l][c]
			if d == 0 {
				continue
			}
			if d < 0 || d > 9 {
				return false
			}
			bit := 1 << d
			if e.linha[l]&bit != 0 || e.coluna[c]&bit != 0 || e.caixa[caixaDe(l, c)]&bit != 0 {
				return false
			}
			e.alterna(l, c, d)
		}
	}
	copia := *g
	if !resolve(&copia, &e) {
		return false
	}
	*g = copia
	return true
}

func resolve(g *Grade, e *estado) bool {
	melhorL, melhorC, melhorMask, melhorN := -1, -1, 0, 10
	for l := 0; l < 9; l++ {
		for c := 0; c < 9; c++ {
			if g[l][c] != 0 {
				continue
			}
			usados := e.linha[l] | e.coluna[c] | e.caixa[caixaDe(l, c)]
			livres := ^usados & 0x3FE // bits 1..9
			n := bits.OnesCount(uint(livres))
			if n == 0 {
				return false
			}
			if n < melhorN {
				melhorL, melhorC, melhorMask, melhorN = l, c, livres, n
			}
		}
	}
	if melhorL == -1 {
		return true // sem células vazias
	}
	for m := melhorMask; m != 0; m &= m - 1 {
		d := bits.TrailingZeros(uint(m))
		g[melhorL][melhorC] = d
		e.alterna(melhorL, melhorC, d)
		if resolve(g, e) {
			return true
		}
		e.alterna(melhorL, melhorC, d)
		g[melhorL][melhorC] = 0
	}
	return false
}
