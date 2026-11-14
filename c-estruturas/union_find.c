#include "union_find.h"
#include <stdint.h>
#include <stdlib.h>

UnionFind *uf_novo(size_t n) {
    UnionFind *u = malloc(sizeof *u);
    if (!u) return NULL;
    u->pai = malloc((n ? n : 1) * sizeof(size_t));
    u->posto = calloc(n ? n : 1, sizeof(size_t));
    u->tamanho = malloc((n ? n : 1) * sizeof(size_t));
    if (!u->pai || !u->posto || !u->tamanho) {
        free(u->pai);
        free(u->posto);
        free(u->tamanho);
        free(u);
        return NULL;
    }
    for (size_t i = 0; i < n; i++) {
        u->pai[i] = i;
        u->tamanho[i] = 1;
    }
    u->n = n;
    u->componentes = n;
    return u;
}

void uf_liberar(UnionFind *u) {
    if (!u) return;
    free(u->pai);
    free(u->posto);
    free(u->tamanho);
    free(u);
}

size_t uf_componentes(const UnionFind *u) { return u->componentes; }

size_t uf_achar(UnionFind *u, size_t x) {
    if (x >= u->n) return SIZE_MAX;
    size_t raiz = x;
    while (u->pai[raiz] != raiz) raiz = u->pai[raiz];
    while (u->pai[x] != raiz) {      /* compressao de caminho */
        size_t p = u->pai[x];
        u->pai[x] = raiz;
        x = p;
    }
    return raiz;
}

bool uf_unir(UnionFind *u, size_t a, size_t b) {
    size_t ra = uf_achar(u, a), rb = uf_achar(u, b);
    if (ra == SIZE_MAX || rb == SIZE_MAX || ra == rb) return false;
    if (u->posto[ra] < u->posto[rb]) {
        size_t t = ra;
        ra = rb;
        rb = t;
    }
    u->pai[rb] = ra;
    u->tamanho[ra] += u->tamanho[rb];
    if (u->posto[ra] == u->posto[rb]) u->posto[ra]++;
    u->componentes--;
    return true;
}

bool uf_conectados(UnionFind *u, size_t a, size_t b) {
    size_t ra = uf_achar(u, a), rb = uf_achar(u, b);
    return ra != SIZE_MAX && ra == rb;
}

size_t uf_tamanho(UnionFind *u, size_t x) {
    size_t r = uf_achar(u, x);
    return r == SIZE_MAX ? 0 : u->tamanho[r];
}
