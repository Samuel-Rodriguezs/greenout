#ifndef UNION_FIND_H
#define UNION_FIND_H
#include <stdbool.h>
#include <stddef.h>

/* Union-Find (conjuntos disjuntos) com uniao por posto e compressao de caminho. */
typedef struct {
    size_t *pai;
    size_t *posto;
    size_t *tamanho;      /* valido apenas nas raizes */
    size_t n;
    size_t componentes;
} UnionFind;

UnionFind *uf_novo(size_t n);
void uf_liberar(UnionFind *u);
size_t uf_componentes(const UnionFind *u);
/* Representante do conjunto de x; SIZE_MAX se x for invalido. */
size_t uf_achar(UnionFind *u, size_t x);
/* Une os conjuntos de a e b. Devolve true se estavam separados. */
bool uf_unir(UnionFind *u, size_t a, size_t b);
bool uf_conectados(UnionFind *u, size_t a, size_t b);
size_t uf_tamanho(UnionFind *u, size_t x);   /* tamanho do conjunto de x (0 se invalido) */

#endif
