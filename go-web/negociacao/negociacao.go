// Pacote negociacao implementa negociação de conteúdo pelo header Accept (com valores q).
package negociacao

import (
	"sort"
	"strconv"
	"strings"
)

type opcao struct {
	tipo, subtipo string
	q             float64
	ordem         int
}

func analisar(accept string) []opcao {
	var ops []opcao
	for i, parte := range strings.Split(accept, ",") {
		parte = strings.TrimSpace(parte)
		if parte == "" {
			continue
		}
		campos := strings.Split(parte, ";")
		mt := strings.ToLower(strings.TrimSpace(campos[0]))
		t, s, ok := strings.Cut(mt, "/")
		if !ok {
			continue
		}
		q := 1.0
		for _, p := range campos[1:] {
			k, v, _ := strings.Cut(strings.TrimSpace(p), "=")
			if k == "q" {
				if f, err := strconv.ParseFloat(v, 64); err == nil {
					q = f
				}
			}
		}
		ops = append(ops, opcao{t, s, q, i})
	}
	return ops
}

// especificidade: 2 exato, 1 tipo/*, 0 */*.
func (o opcao) combina(oferta string) (int, bool) {
	t, s, _ := strings.Cut(strings.ToLower(oferta), "/")
	switch {
	case o.tipo == t && o.subtipo == s:
		return 2, true
	case o.tipo == t && o.subtipo == "*":
		return 1, true
	case o.tipo == "*" && o.subtipo == "*":
		return 0, true
	}
	return 0, false
}

// Escolher retorna a melhor oferta para o header Accept, ou "" se nenhuma é
// aceitável. Accept vazio escolhe a primeira oferta. Empates favorecem a ordem
// das ofertas.
func Escolher(accept string, ofertas []string) string {
	if len(ofertas) == 0 {
		return ""
	}
	ops := analisar(accept)
	if len(ops) == 0 {
		return ofertas[0]
	}
	type pontuada struct {
		oferta string
		q      float64
		espec  int
		idx    int
	}
	var cands []pontuada
	for i, of := range ofertas {
		melhor := pontuada{oferta: of, q: -1, idx: i}
		for _, o := range ops {
			if e, ok := o.combina(of); ok && e >= melhor.espec && (melhor.q < 0 || e > melhor.espec) {
				melhor.q, melhor.espec = o.q, e
			}
		}
		if melhor.q > 0 {
			cands = append(cands, melhor)
		}
	}
	if len(cands) == 0 {
		return ""
	}
	sort.SliceStable(cands, func(a, b int) bool { return cands[a].q > cands[b].q })
	return cands[0].oferta
}
