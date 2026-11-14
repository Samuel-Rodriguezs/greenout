#include <assert.h>
#include <stdio.h>
#include "grafo.h"

static void confere(const size_t *obtido, size_t n, const size_t *esperado) {
    for (size_t i = 0; i < n; i++) assert(obtido[i] == esperado[i]);
}

int main(void) {
    size_t ordem[16];

    /* grafo vazio e de um unico vertice */
    Grafo *g = grafo_novo(0, false);
    assert(grafo_vertices(g) == 0 && grafo_bfs(g, 0, ordem) == 0);
    assert(grafo_distancia(g, 0, 0) == -1);
    grafo_liberar(g);
    g = grafo_novo(1, false);
    assert(grafo_bfs(g, 0, ordem) == 1 && ordem[0] == 0);
    assert(grafo_adicionar_aresta(g, 0, 0) && grafo_arestas(g) == 1); /* laco */
    assert(grafo_dfs(g, 0, ordem) == 1);
    grafo_liberar(g);

    /* nao direcionado:
     *   0 - 1 - 3
     *   |   |
     *   2 - 4      5 isolado, 6 - 7 outra componente */
    g = grafo_novo(8, false);
    assert(grafo_adicionar_aresta(g, 0, 1) && grafo_adicionar_aresta(g, 0, 2));
    assert(grafo_adicionar_aresta(g, 1, 3) && grafo_adicionar_aresta(g, 1, 4));
    assert(grafo_adicionar_aresta(g, 2, 4) && grafo_adicionar_aresta(g, 6, 7));
    assert(!grafo_adicionar_aresta(g, 1, 0));      /* repetida (nao direcionado) */
    assert(!grafo_adicionar_aresta(g, 0, 8));      /* fora do intervalo */
    assert(grafo_arestas(g) == 6);
    assert(grafo_tem_aresta(g, 4, 1) && !grafo_tem_aresta(g, 3, 4));

    size_t bfs[] = {0, 1, 2, 3, 4};
    assert(grafo_bfs(g, 0, ordem) == 5);
    confere(ordem, 5, bfs);
    size_t dfs[] = {0, 1, 3, 4, 2};
    assert(grafo_dfs(g, 0, ordem) == 5);
    confere(ordem, 5, dfs);
    assert(grafo_bfs(g, 5, ordem) == 1);
    assert(grafo_bfs(g, 99, ordem) == 0 && grafo_dfs(g, 99, ordem) == 0);
    assert(grafo_distancia(g, 0, 4) == 2 && grafo_distancia(g, 3, 2) == 3);
    assert(grafo_distancia(g, 0, 0) == 0);
    assert(grafo_distancia(g, 0, 7) == -1);
    grafo_liberar(g);

    /* direcionado: 0 -> 1 -> 2, 2 -> 0, 3 -> 0 (ninguem chega em 3) */
    g = grafo_novo(4, true);
    assert(grafo_adicionar_aresta(g, 0, 1) && grafo_adicionar_aresta(g, 1, 2));
    assert(grafo_adicionar_aresta(g, 2, 0) && grafo_adicionar_aresta(g, 3, 0));
    assert(grafo_adicionar_aresta(g, 1, 0));       /* sentido oposto e outra aresta */
    assert(grafo_arestas(g) == 5);
    assert(grafo_bfs(g, 0, ordem) == 3);
    assert(grafo_distancia(g, 0, 3) == -1 && grafo_distancia(g, 3, 2) == 3);
    grafo_liberar(g);
    grafo_liberar(NULL);
    puts("grafo ok");
    return 0;
}
