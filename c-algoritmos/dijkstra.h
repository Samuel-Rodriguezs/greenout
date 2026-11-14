#ifndef DIJKSTRA_H
#define DIJKSTRA_H
#include <stddef.h>

/* Grafo dirigido ponderado (lista de adjacencia) e Dijkstra com heap
 * binario proprio. Pesos devem ser >= 0. */
typedef struct Grafo Grafo;

#define DIJKSTRA_INF ((long long)4611686018427387903LL)   /* "infinito" (2^62 - 1) */

Grafo *grafo_criar(size_t n_vertices);
void grafo_liberar(Grafo *g);

/* Adiciona aresta u -> v. Retorna 0 em sucesso; -1 se vertice invalido,
 * peso negativo ou falta de memoria. Para nao-dirigido, adicione as duas. */
int grafo_adicionar_aresta(Grafo *g, size_t u, size_t v, long long peso);

/* Menores distancias a partir de origem. dist (n_vertices posicoes) recebe
 * DIJKSTRA_INF para vertices inalcancaveis; pai (opcional, pode ser NULL)
 * recebe o predecessor ou -1. Retorna 0 em sucesso, -1 se origem invalida
 * ou falta de memoria. */
int dijkstra(const Grafo *g, size_t origem, long long *dist, long *pai);

#endif
