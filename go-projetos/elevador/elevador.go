// Pacote elevador simula um elevador que atende chamadas com a estratégia
// "varredura": continua na direção atual enquanto houver paradas à frente.
package elevador

import (
	"errors"
	"fmt"
)

// Direção do movimento.
type Direcao int

const (
	Parado Direcao = iota
	Subindo
	Descendo
)

// ErrAndarInvalido indica um andar fora do prédio.
var ErrAndarInvalido = errors.New("elevador: andar inválido")

// Elevador atende paradas em andares de 0 até Topo.
type Elevador struct {
	Andar   int
	Dir     Direcao
	Topo    int
	paradas map[int]bool
	Log     []string // andares onde as portas abriram, em ordem
}

// Novo cria um elevador no térreo (andar 0) de um prédio com topo+1 andares.
func Novo(topo int) (*Elevador, error) {
	if topo <= 0 {
		return nil, fmt.Errorf("%w: topo %d", ErrAndarInvalido, topo)
	}
	return &Elevador{Topo: topo, paradas: map[int]bool{}}, nil
}

// Chamar registra uma parada em um andar.
func (e *Elevador) Chamar(andar int) error {
	if andar < 0 || andar > e.Topo {
		return fmt.Errorf("%w: %d", ErrAndarInvalido, andar)
	}
	e.paradas[andar] = true
	return nil
}

// Pendentes informa se ainda há paradas a atender.
func (e *Elevador) Pendentes() bool { return len(e.paradas) > 0 }

func (e *Elevador) haParadaAdiante(d Direcao) bool {
	for a := range e.paradas {
		if (d == Subindo && a > e.Andar) || (d == Descendo && a < e.Andar) {
			return true
		}
	}
	return false
}

// Passo avança o relógio em uma unidade: abre a porta se há parada no
// andar atual; senão, move um andar. Devolve true se as portas abriram.
func (e *Elevador) Passo() bool {
	if e.paradas[e.Andar] {
		delete(e.paradas, e.Andar)
		e.Log = append(e.Log, fmt.Sprint(e.Andar))
		if !e.Pendentes() {
			e.Dir = Parado
		}
		return true
	}
	if !e.Pendentes() {
		e.Dir = Parado
		return false
	}
	// Mantém a direção se houver paradas adiante; senão, inverte.
	switch {
	case e.Dir == Subindo && e.haParadaAdiante(Subindo):
	case e.Dir == Descendo && e.haParadaAdiante(Descendo):
	case e.haParadaAdiante(Subindo):
		e.Dir = Subindo
	default:
		e.Dir = Descendo
	}
	if e.Dir == Subindo {
		e.Andar++
	} else {
		e.Andar--
	}
	return false
}

// Executar roda passos até esvaziar as paradas e devolve o número de passos.
func (e *Elevador) Executar() int {
	n := 0
	for e.Pendentes() {
		e.Passo()
		n++
	}
	return n
}
