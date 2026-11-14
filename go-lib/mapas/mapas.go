// Pacote mapas oferece utilitários genéricos para maps.
package mapas

import (
	"cmp"
	"slices"
)

// Chaves devolve as chaves em ordem crescente (determinística).
func Chaves[K cmp.Ordered, V any](m map[K]V) []K {
	r := make([]K, 0, len(m))
	for k := range m {
		r = append(r, k)
	}
	slices.Sort(r)
	return r
}

// Valores devolve os valores ordenados pela ordem das chaves.
func Valores[K cmp.Ordered, V any](m map[K]V) []V {
	r := make([]V, 0, len(m))
	for _, k := range Chaves(m) {
		r = append(r, m[k])
	}
	return r
}

// Copiar faz uma cópia rasa do mapa. Mapa nil resulta em mapa vazio.
func Copiar[K comparable, V any](m map[K]V) map[K]V {
	r := make(map[K]V, len(m))
	for k, v := range m {
		r[k] = v
	}
	return r
}

// Mesclar combina mapas; em chaves repetidas vence o último.
func Mesclar[K comparable, V any](ms ...map[K]V) map[K]V {
	r := map[K]V{}
	for _, m := range ms {
		for k, v := range m {
			r[k] = v
		}
	}
	return r
}

// Inverter troca chaves por valores; em valores repetidos o resultado
// é indefinido quanto a qual chave vence.
func Inverter[K, V comparable](m map[K]V) map[V]K {
	r := make(map[V]K, len(m))
	for k, v := range m {
		r[v] = k
	}
	return r
}

// FiltrarMapa mantém apenas as entradas aceitas pelo predicado.
func FiltrarMapa[K comparable, V any](m map[K]V, f func(K, V) bool) map[K]V {
	r := map[K]V{}
	for k, v := range m {
		if f(k, v) {
			r[k] = v
		}
	}
	return r
}
