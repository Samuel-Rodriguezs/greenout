#include "dijkstra.h"
#include <stdlib.h>

typedef struct Aresta {
    size_t destino;
    long long peso;
    struct Aresta *prox;
} Aresta;

struct Grafo {
    size_t n;
    Aresta **adj;
};

Grafo *grafo_criar(size_t n) {
    Grafo *g = malloc(sizeof *g);
    if (!g) return NULL;
    g->n = n;
    g->adj = calloc(n ? n : 1, sizeof *g->adj);
    if (!g->adj) { free(g); return NULL; }
    return g;
}

void grafo_liberar(Grafo *g) {
    if (!g) return;
    for (size_t i = 0; i < g->n; i++) {
        Aresta *e = g->adj[i];
        while (e) { Aresta *p = e->prox; free(e); e = p; }
    }
    free(g->adj);
    free(g);
}

int grafo_adicionar_aresta(Grafo *g, size_t u, size_t v, long long peso) {
    if (u >= g->n || v >= g->n || peso < 0) return -1;
    Aresta *e = malloc(sizeof *e);
    if (!e) return -1;
    e->destino = v;
    e->peso = peso;
    e->prox = g->adj[u];
    g->adj[u] = e;
    return 0;
}

/* ---- heap binario minimo de (distancia, vertice), com remocao preguicosa ---- */
typedef struct { long long d; size_t v; } Item;
typedef struct { Item *a; size_t n, cap; } Heap;

static int heap_push(Heap *h, long long d, size_t v) {
    if (h->n == h->cap) {
        size_t nc = h->cap ? h->cap * 2 : 16;
        Item *na = realloc(h->a, nc * sizeof *na);
        if (!na) return -1;
        h->a = na;
        h->cap = nc;
    }
    size_t i = h->n++;
    while (i > 0) {                          /* sobe */
        size_t p = (i - 1) / 2;
        if (h->a[p].d <= d) break;
        h->a[i] = h->a[p];
        i = p;
    }
    h->a[i].d = d;
    h->a[i].v = v;
    return 0;
}

static Item heap_pop(Heap *h) {
    Item topo = h->a[0];
    Item ult = h->a[--h->n];
    size_t i = 0;
    for (;;) {                               /* desce */
        size_t f = 2 * i + 1;
        if (f >= h->n) break;
        if (f + 1 < h->n && h->a[f + 1].d < h->a[f].d) f++;
        if (h->a[f].d >= ult.d) break;
        h->a[i] = h->a[f];
        i = f;
    }
    if (h->n > 0) h->a[i] = ult;
    return topo;
}

int dijkstra(const Grafo *g, size_t origem, long long *dist, long *pai) {
    if (origem >= g->n) return -1;
    for (size_t i = 0; i < g->n; i++) {
        dist[i] = DIJKSTRA_INF;
        if (pai) pai[i] = -1;
    }
    Heap h = {NULL, 0, 0};
    dist[origem] = 0;
    if (heap_push(&h, 0, origem) != 0) return -1;
    while (h.n > 0) {
        Item it = heap_pop(&h);
        if (it.d > dist[it.v]) continue;     /* entrada obsoleta */
        for (const Aresta *e = g->adj[it.v]; e; e = e->prox) {
            long long nd = it.d + e->peso;
            if (nd < dist[e->destino]) {
                dist[e->destino] = nd;
                if (pai) pai[e->destino] = (long)it.v;
                if (heap_push(&h, nd, e->destino) != 0) { free(h.a); return -1; }
            }
        }
    }
    free(h.a);
    return 0;
}
