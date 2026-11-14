#include <assert.h>
#include <stdio.h>
#include "mochila.h"

int main(void) {
    int p[] = {1, 3, 4, 5};
    int v[] = {1, 4, 5, 7};
    assert(mochila(p, v, 4, 7) == 9);     /* itens 3+4 */
    assert(mochila(p, v, 4, 0) == 0);     /* capacidade zero */
    assert(mochila(p, v, 0, 10) == 0);    /* sem itens */
    assert(mochila(p, v, 4, 1) == 1);
    assert(mochila(p, v, 4, 13) == 17);   /* cabe tudo */
    assert(mochila(p, v, 4, 100) == 17);
    int p2[] = {10, 20, 30};
    int v2[] = {60, 100, 120};
    assert(mochila(p2, v2, 3, 50) == 220);
    assert(mochila(p2, v2, 3, 5) == 0);   /* nada cabe */
    int p3[] = {5};
    int v3[] = {10};
    assert(mochila(p3, v3, 1, 5) == 10);
    assert(mochila(p3, v3, 1, 4) == 0);   /* cada item so uma vez */
    assert(mochila(p3, v3, 1, 10) == 10);
    /* entradas invalidas */
    int pz[] = {0};
    assert(mochila(pz, v3, 1, 5) == -1);
    assert(mochila(p3, v3, 1, -1) == -1);
    puts("mochila ok");
    return 0;
}
