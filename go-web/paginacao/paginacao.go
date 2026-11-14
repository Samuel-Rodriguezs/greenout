// Pacote paginacao extrai parâmetros page/per_page da query e fatia resultados,
// gerando metadados e o header Link.
package paginacao

import (
	"fmt"
	"net/http"
	"net/url"
	"strconv"
)

// Params são os parâmetros normalizados.
type Params struct {
	Pagina, PorPagina int
}

// Meta descreve o resultado paginado.
type Meta struct {
	Pagina       int `json:"pagina"`
	PorPagina    int `json:"por_pagina"`
	Total        int `json:"total"`
	TotalPaginas int `json:"total_paginas"`
}

const (
	padraoPorPagina = 10
	maxPorPagina    = 100
)

// Ler extrai page e per_page; valores inválidos voltam ao padrão e per_page é
// limitado a 100.
func Ler(q url.Values) Params {
	p := Params{Pagina: 1, PorPagina: padraoPorPagina}
	if n, err := strconv.Atoi(q.Get("page")); err == nil && n > 0 {
		p.Pagina = n
	}
	if n, err := strconv.Atoi(q.Get("per_page")); err == nil && n > 0 {
		p.PorPagina = min(n, maxPorPagina)
	}
	return p
}

// Fatiar devolve a página solicitada de itens e seus metadados. Páginas além
// do fim retornam fatia vazia.
func Fatiar[T any](itens []T, p Params) ([]T, Meta) {
	total := len(itens)
	paginas := (total + p.PorPagina - 1) / p.PorPagina
	m := Meta{Pagina: p.Pagina, PorPagina: p.PorPagina, Total: total, TotalPaginas: paginas}
	ini := (p.Pagina - 1) * p.PorPagina
	if ini >= total {
		return []T{}, m
	}
	return itens[ini:min(ini+p.PorPagina, total)], m
}

// Link monta o header Link (RFC 8288) com first/prev/next/last.
func Link(r *http.Request, m Meta) string {
	montar := func(pag int, rel string) string {
		q := r.URL.Query()
		q.Set("page", strconv.Itoa(pag))
		q.Set("per_page", strconv.Itoa(m.PorPagina))
		return fmt.Sprintf(`<%s?%s>; rel="%s"`, r.URL.Path, q.Encode(), rel)
	}
	if m.TotalPaginas == 0 {
		return ""
	}
	partes := []string{montar(1, "first")}
	if m.Pagina > 1 {
		partes = append(partes, montar(min(m.Pagina-1, m.TotalPaginas), "prev"))
	}
	if m.Pagina < m.TotalPaginas {
		partes = append(partes, montar(m.Pagina+1, "next"))
	}
	partes = append(partes, montar(m.TotalPaginas, "last"))
	res := partes[0]
	for _, p := range partes[1:] {
		res += ", " + p
	}
	return res
}
