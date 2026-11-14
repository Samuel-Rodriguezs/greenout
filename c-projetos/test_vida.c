#include <assert.h>
#include <stdio.h>
#include "vida.h"

int main(void) {
    /* Blinker: oscila com periodo 2. */
    Vida *v = vida_criar(5, 5);
    assert(v);
    vida_set(v, 2, 1, 1); vida_set(v, 2, 2, 1); vida_set(v, 2, 3, 1);
    vida_passo(v);
    assert(vida_get(v, 1, 2) && vida_get(v, 2, 2) && vida_get(v, 3, 2));
    assert(!vida_get(v, 2, 1) && vida_populacao(v) == 3);
    vida_passo(v);
    assert(vida_get(v, 2, 1) && vida_get(v, 2, 3));
    vida_liberar(v);

    /* Planador em grade 6x6 volta ao mesmo formato deslocado (1,1) apos 4 passos. */
    v = vida_criar(6, 6);
    int g[5][2] = {{0, 1}, {1, 2}, {2, 0}, {2, 1}, {2, 2}};
    for (int i = 0; i < 5; i++) vida_set(v, g[i][0], g[i][1], 1);
    for (int i = 0; i < 4; i++) vida_passo(v);
    for (int i = 0; i < 5; i++) assert(vida_get(v, g[i][0] + 1, g[i][1] + 1));
    assert(vida_populacao(v) == 5);
    /* Wrap: indices negativos acessam o outro lado. */
    vida_set(v, -1, -1, 1);
    assert(vida_get(v, 5, 5) == 1);
    vida_liberar(v);
    assert(vida_criar(0, 3) == NULL);
    puts("vida ok");
    return 0;
}
