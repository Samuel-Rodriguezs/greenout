// Pacote agregacao resume listas de prefixos IPv4 no menor conjunto
// equivalente (supernetting / route summarization).
package agregacao

import (
	"sort"

	"greenout/net/cidr"
)

// Agregar devolve o conjunto mínimo de prefixos que cobre exatamente os
// mesmos endereços da entrada: remove duplicados e prefixos contidos em
// outros e funde irmãos adjacentes (ex.: 10.0.0.0/25 + 10.0.0.128/25 vira
// 10.0.0.0/24). A saída vem ordenada por endereço base. A entrada não é alterada.
func Agregar(entrada []cidr.Prefixo) []cidr.Prefixo {
	if len(entrada) == 0 {
		return nil
	}
	ord := append([]cidr.Prefixo(nil), entrada...)
	sort.Slice(ord, func(i, j int) bool {
		if ord[i].Base != ord[j].Base {
			return ord[i].Base < ord[j].Base
		}
		return ord[i].Tam < ord[j].Tam // o mais genérico primeiro
	})

	var pilha []cidr.Prefixo
	for _, p := range ord {
		if n := len(pilha); n > 0 && pilha[n-1].ContemPrefixo(p) {
			continue
		}
		pilha = append(pilha, p)
		// Funde enquanto os dois topos forem irmãos.
		for n := len(pilha); n >= 2; n = len(pilha) {
			a, b := pilha[n-2], pilha[n-1]
			if a.Tam != b.Tam || a.Tam == 0 || a.Base == b.Base || a.Pai() != b.Pai() {
				break
			}
			pilha = append(pilha[:n-2], a.Pai())
		}
	}
	return pilha
}

// Cobre informa se algum prefixo do conjunto contém p.
func Cobre(conjunto []cidr.Prefixo, p cidr.Prefixo) bool {
	for _, q := range conjunto {
		if q.ContemPrefixo(p) {
			return true
		}
	}
	return false
}
