// Pacote vida implementa o Jogo da Vida de Conway em grade toroidal.
package vida

import (
	"errors"
	"strings"
)

// ErrGrade indica uma grade inválida (vazia ou irregular).
var ErrGrade = errors.New("vida: grade inválida")

// Grade é uma matriz de células vivas (true) ou mortas (false).
type Grade struct {
	l, c  int
	celas [][]bool
}

// Nova cria uma grade vazia com l linhas e c colunas.
func Nova(l, c int) (*Grade, error) {
	if l <= 0 || c <= 0 {
		return nil, ErrGrade
	}
	g := &Grade{l: l, c: c, celas: make([][]bool, l)}
	for i := range g.celas {
		g.celas[i] = make([]bool, c)
	}
	return g, nil
}

// DeTexto cria uma grade a partir de linhas onde '#' é vivo e '.' é morto.
func DeTexto(s string) (*Grade, error) {
	linhas := strings.Split(strings.TrimSpace(s), "\n")
	g, err := Nova(len(linhas), len(strings.TrimSpace(linhas[0])))
	if err != nil {
		return nil, err
	}
	for i, ln := range linhas {
		ln = strings.TrimSpace(ln)
		if len(ln) != g.c {
			return nil, ErrGrade
		}
		for j, ch := range ln {
			g.celas[i][j] = ch == '#'
		}
	}
	return g, nil
}

// String desenha a grade no mesmo formato aceito por DeTexto.
func (g *Grade) String() string {
	var sb strings.Builder
	for i, linha := range g.celas {
		if i > 0 {
			sb.WriteByte('\n')
		}
		for _, v := range linha {
			if v {
				sb.WriteByte('#')
			} else {
				sb.WriteByte('.')
			}
		}
	}
	return sb.String()
}

// Viva informa se a célula está viva; coordenadas dão a volta (toroide).
func (g *Grade) Viva(i, j int) bool {
	return g.celas[((i%g.l)+g.l)%g.l][((j%g.c)+g.c)%g.c]
}

func (g *Grade) vizinhos(i, j int) int {
	n := 0
	for di := -1; di <= 1; di++ {
		for dj := -1; dj <= 1; dj++ {
			if (di != 0 || dj != 0) && g.Viva(i+di, j+dj) {
				n++
			}
		}
	}
	return n
}

// Proxima devolve a geração seguinte sem alterar a atual.
func (g *Grade) Proxima() *Grade {
	novo, _ := Nova(g.l, g.c)
	for i := 0; i < g.l; i++ {
		for j := 0; j < g.c; j++ {
			n := g.vizinhos(i, j)
			novo.celas[i][j] = n == 3 || (g.celas[i][j] && n == 2)
		}
	}
	return novo
}

// Populacao conta as células vivas.
func (g *Grade) Populacao() int {
	n := 0
	for _, linha := range g.celas {
		for _, v := range linha {
			if v {
				n++
			}
		}
	}
	return n
}
