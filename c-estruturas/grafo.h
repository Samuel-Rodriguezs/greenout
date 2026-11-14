#ifndef GRAFO_H
#define GRAFO_H
#include <stdbool.h>
#include <stddef.h>

/* Grafo (nao ponderado) com lista de adjacencia. Vertices 0..n-1.
 * Pode ser direcionado ou nao. Arestas repetidas sao ignoradas. */
typedef struct Adj {
    size_t destino;
    struct Adj *prox;
} Adj;

typedef struct {
    size_t n;
    bool direcionado;
    Adj **adj;
    size_t arestas;
} Grafo;

Grafo *grafo_novo(size_t n, bool direcionado);
void grafo_liberar(Grafo *g);
size_t grafo_vertices(const Grafo *g);
size_t grafo_arestas(const Grafo *g);
bool grafo_adicionar_aresta(Grafo *g, size_t u, size_t v); /* false: fora do intervalo/repetida */
bool grafo_tem_aresta(const Grafo *g, size_t u, size_t v);
/* Percursos a partir de origem. Gravam a ordem de visita em ordem[] (capacidade
 * g->n) e devolvem quantos vertices foram visitados (0 se origem invalida).
 * Vizinhos sao visitados em ordem crescente de indice. */
size_t grafo_bfs(const Grafo *g, size_t origem, size_t *ordem);
size_t grafo_dfs(const Grafo *g, size_t origem, size_t *ordem);
/* Distancia minima (em arestas) de origem a destino; -1 se inalcancavel/invalido. */
long grafo_distancia(const Grafo *g, size_t origem, size_t destino);

#endif
