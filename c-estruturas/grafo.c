#include "grafo.h"
#include <stdlib.h>

Grafo *grafo_novo(size_t n, bool direcionado) {
    Grafo *g = malloc(sizeof *g);
    if (!g) return NULL;
    g->adj = n ? calloc(n, sizeof *g->adj) : NULL;
    if (n && !g->adj) {
        free(g);
        return NULL;
    }
    g->n = n;
    g->direcionado = direcionado;
    g->arestas = 0;
    return g;
}

void grafo_liberar(Grafo *g) {
    if (!g) return;
    for (size_t i = 0; i < g->n; i++) {
        Adj *a = g->adj[i];
        while (a) {
            Adj *p = a->prox;
            free(a);
            a = p;
        }
    }
    free(g->adj);
    free(g);
}

size_t grafo_vertices(const Grafo *g) { return g->n; }
size_t grafo_arestas(const Grafo *g) { return g->arestas; }

bool grafo_tem_aresta(const Grafo *g, size_t u, size_t v) {
    if (u >= g->n || v >= g->n) return false;
    for (const Adj *a = g->adj[u]; a; a = a->prox)
        if (a->destino == v) return true;
    return false;
}

/* Insere mantendo a lista ordenada por destino (percursos deterministicos). */
static bool inserir_adj(Grafo *g, size_t u, size_t v) {
    Adj **pp = &g->adj[u];
    while (*pp && (*pp)->destino < v) pp = &(*pp)->prox;
    Adj *a = malloc(sizeof *a);
    if (!a) return false;
    a->destino = v;
    a->prox = *pp;
    *pp = a;
    return true;
}

bool grafo_adicionar_aresta(Grafo *g, size_t u, size_t v) {
    if (u >= g->n || v >= g->n || grafo_tem_aresta(g, u, v)) return false;
    if (!inserir_adj(g, u, v)) return false;
    if (!g->direcionado && u != v && !inserir_adj(g, v, u)) return false;
    g->arestas++;
    return true;
}

size_t grafo_bfs(const Grafo *g, size_t origem, size_t *ordem) {
    if (origem >= g->n) return 0;
    bool *vis = calloc(g->n, sizeof *vis);
    if (!vis) return 0;
    size_t ini = 0, fim = 0;     /* a propria saida serve de fila */
    ordem[fim++] = origem;
    vis[origem] = true;
    while (ini < fim) {
        size_t u = ordem[ini++];
        for (const Adj *a = g->adj[u]; a; a = a->prox) {
            if (!vis[a->destino]) {
                vis[a->destino] = true;
                ordem[fim++] = a->destino;
            }
        }
    }
    free(vis);
    return fim;
}

/* DFS iterativa com pilha explicita (evita estouro de pilha em grafos grandes). */
size_t grafo_dfs(const Grafo *g, size_t origem, size_t *ordem) {
    if (origem >= g->n) return 0;
    bool *vis = calloc(g->n, sizeof *vis);
    const Adj **prox = calloc(g->n, sizeof *prox);   /* proximo vizinho a tentar */
    size_t *pilha = malloc(g->n * sizeof *pilha);
    if (!vis || !prox || !pilha) {
        free(vis);
        free(prox);
        free(pilha);
        return 0;
    }
    size_t topo = 0, k = 0;
    pilha[topo++] = origem;
    vis[origem] = true;
    prox[origem] = g->adj[origem];
    ordem[k++] = origem;
    while (topo > 0) {
        size_t u = pilha[topo - 1];
        const Adj *a = prox[u];
        while (a && vis[a->destino]) a = a->prox;
        if (!a) {
            topo--;
            continue;
        }
        prox[u] = a->prox;
        size_t v = a->destino;
        vis[v] = true;
        prox[v] = g->adj[v];
        ordem[k++] = v;
        pilha[topo++] = v;
    }
    free(vis);
    free(prox);
    free(pilha);
    return k;
}

long grafo_distancia(const Grafo *g, size_t origem, size_t destino) {
    if (origem >= g->n || destino >= g->n) return -1;
    long *dist = malloc(g->n * sizeof *dist);
    size_t *fila = malloc(g->n * sizeof *fila);
    if (!dist || !fila) {
        free(dist);
        free(fila);
        return -1;
    }
    for (size_t i = 0; i < g->n; i++) dist[i] = -1;
    size_t ini = 0, fim = 0;
    fila[fim++] = origem;
    dist[origem] = 0;
    while (ini < fim) {
        size_t u = fila[ini++];
        for (const Adj *a = g->adj[u]; a; a = a->prox) {
            if (dist[a->destino] < 0) {
                dist[a->destino] = dist[u] + 1;
                fila[fim++] = a->destino;
            }
        }
    }
    long r = dist[destino];
    free(dist);
    free(fila);
    return r;
}
