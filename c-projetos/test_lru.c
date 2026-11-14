#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "lru.h"

int main(void) {
    Lru *c = lru_criar(3);
    assert(c && lru_mais_antiga(c) == NULL);
    lru_put(c, "a", 1); lru_put(c, "b", 2); lru_put(c, "c", 3);
    assert(lru_tamanho(c) == 3 && strcmp(lru_mais_antiga(c), "a") == 0);

    int v;
    assert(lru_get(c, "a", &v) && v == 1);      /* a vira a mais recente */
    assert(strcmp(lru_mais_antiga(c), "b") == 0);
    lru_put(c, "d", 4);                         /* expulsa b */
    assert(!lru_get(c, "b", &v));
    assert(lru_get(c, "c", &v) && v == 3);
    assert(lru_tamanho(c) == 3);

    lru_put(c, "a", 10);                        /* atualiza sem crescer */
    assert(lru_tamanho(c) == 3);
    assert(lru_get(c, "a", &v) && v == 10);
    assert(strcmp(lru_mais_antiga(c), "d") == 0);

    /* Carga: so as 3 ultimas chaves sobrevivem. */
    for (int i = 0; i < 1000; i++) {
        char k[16];
        sprintf(k, "k%d", i);
        assert(lru_put(c, k, i) == 0);
    }
    assert(lru_tamanho(c) == 3);
    assert(lru_get(c, "k999", &v) && v == 999);
    assert(!lru_get(c, "k996", &v));
    lru_liberar(c);
    assert(lru_criar(0) == NULL);
    puts("lru ok");
    return 0;
}
