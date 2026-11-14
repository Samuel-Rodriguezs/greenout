#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include "dijkstra.h"

int main(void) {
    /* grafo classico: 0->1 (7), 0->2 (9), 0->5 (14), 1->2 (10), 1->3 (15),
       2->3 (11), 2->5 (2), 3->4 (6), 5->4 (9); vertice 6 isolado */
    Grafo *g = grafo_criar(7);
    assert(g);
    size_t arestas[][3] = {{0,1,7},{0,2,9},{0,5,14},{1,2,10},{1,3,15},
                           {2,3,11},{2,5,2},{3,4,6},{5,4,9}};
    for (int i = 0; i < 9; i++)
        assert(grafo_adicionar_aresta(g, arestas[i][0], arestas[i][1], (long long)arestas[i][2]) == 0);
    long long dist[7];
    long pai[7];
    assert(dijkstra(g, 0, dist, pai) == 0);
    assert(dist[0] == 0 && dist[1] == 7 && dist[2] == 9 && dist[3] == 20);
    assert(dist[4] == 20 && dist[5] == 11);
    assert(dist[6] == DIJKSTRA_INF && pai[6] == -1);   /* inalcancavel */
    assert(pai[0] == -1 && pai[5] == 2 && pai[4] == 5 && pai[2] == 0);
    assert(dijkstra(g, 0, dist, NULL) == 0 && dist[4] == 20);   /* pai opcional */
    /* origem diferente: grafo dirigido, 3 so alcanca 4 */
    assert(dijkstra(g, 3, dist, NULL) == 0);
    assert(dist[3] == 0 && dist[4] == 6 && dist[0] == DIJKSTRA_INF);
    /* entradas invalidas */
    assert(dijkstra(g, 7, dist, NULL) == -1);
    assert(grafo_adicionar_aresta(g, 0, 7, 1) == -1);
    assert(grafo_adicionar_aresta(g, 9, 0, 1) == -1);
    assert(grafo_adicionar_aresta(g, 0, 1, -5) == -1);
    grafo_liberar(g);

    /* vertice unico, arestas de peso zero, laco e arestas paralelas */
    g = grafo_criar(1);
    assert(g && dijkstra(g, 0, dist, pai) == 0 && dist[0] == 0 && pai[0] == -1);
    assert(grafo_adicionar_aresta(g, 0, 0, 3) == 0);
    assert(dijkstra(g, 0, dist, pai) == 0 && dist[0] == 0);
    grafo_liberar(g);
    g = grafo_criar(3);
    assert(g);
    grafo_adicionar_aresta(g, 0, 1, 5);
    grafo_adicionar_aresta(g, 0, 1, 2);        /* paralela mais barata */
    grafo_adicionar_aresta(g, 1, 2, 0);        /* peso zero */
    assert(dijkstra(g, 0, dist, pai) == 0);
    assert(dist[1] == 2 && dist[2] == 2 && pai[2] == 1);
    grafo_liberar(g);

    /* grafo vazio: nenhuma origem valida */
    g = grafo_criar(0);
    assert(g && dijkstra(g, 0, dist, NULL) == -1);
    grafo_liberar(g);
    grafo_liberar(NULL);

    /* grafo grande (cadeia + atalhos) confere com a formula fechada */
    enum { N = 20000 };
    long long *d = malloc(N * sizeof *d);
    assert(d);
    g = grafo_criar(N);
    assert(g);
    for (size_t i = 0; i + 1 < N; i++) {
        assert(grafo_adicionar_aresta(g, i, i + 1, 3) == 0);
        if (i + 2 < N) assert(grafo_adicionar_aresta(g, i, i + 2, 5) == 0);  /* 2.5 por passo */
    }
    assert(dijkstra(g, 0, d, NULL) == 0);
    assert(d[1] == 3 && d[2] == 5 && d[3] == 8 && d[4] == 10);
    assert(d[N - 1] == (long long)((N - 1) / 2) * 5 + (((N - 1) % 2) ? 3 : 0));
    grafo_liberar(g);
    free(d);
    puts("dijkstra ok");
    return 0;
}
