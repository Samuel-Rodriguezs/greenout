#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include "union_find.h"

int main(void) {
    UnionFind *u = uf_novo(0);                 /* vazio */
    assert(uf_componentes(u) == 0 && uf_achar(u, 0) == SIZE_MAX);
    assert(!uf_unir(u, 0, 0) && uf_tamanho(u, 0) == 0);
    uf_liberar(u);

    u = uf_novo(10);
    assert(uf_componentes(u) == 10);
    assert(!uf_conectados(u, 1, 2) && uf_conectados(u, 3, 3));
    assert(uf_unir(u, 1, 2) && uf_unir(u, 3, 4) && uf_unir(u, 2, 4));
    assert(!uf_unir(u, 1, 3));                 /* ja conectados */
    assert(!uf_unir(u, 1, 10) && !uf_conectados(u, 1, 10)); /* invalido */
    assert(uf_componentes(u) == 7);
    assert(uf_conectados(u, 1, 4) && !uf_conectados(u, 1, 5));
    assert(uf_tamanho(u, 3) == 4 && uf_tamanho(u, 9) == 1);
    for (size_t i = 0; i < 9; i++) uf_unir(u, i, i + 1);
    assert(uf_componentes(u) == 1 && uf_tamanho(u, 0) == 10);
    uf_liberar(u);

    /* cadeia longa: compressao de caminho nao pode estourar a pilha */
    size_t n = 100000;
    u = uf_novo(n);
    for (size_t i = 0; i + 1 < n; i++) assert(uf_unir(u, i, i + 1));
    assert(uf_componentes(u) == 1 && uf_conectados(u, 0, n - 1));
    uf_liberar(u);
    uf_liberar(NULL);
    puts("union_find ok");
    return 0;
}
