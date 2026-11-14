#include <assert.h>
#include <stdio.h>

#include "substituicao.h"

#define N(a) (sizeof(a) / sizeof((a)[0]))

int main(void) {
    /* cadeia classica de Silberschatz, 3 quadros: FIFO=15, LRU=12, otimo=9 */
    int a[] = {7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1};
    assert(subst_fifo(a, N(a), 3) == 15);
    assert(subst_lru(a, N(a), 3) == 12);
    assert(subst_otimo(a, N(a), 3) == 9);
    /* relogio (calculado a mao, quadros iniciais preenchidos em ordem) */
    assert(subst_clock(a, N(a), 3) == 14);

    /* anomalia de Belady: FIFO piora com mais quadros */
    int b[] = {1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5};
    assert(subst_fifo(b, N(b), 3) == 9);
    assert(subst_fifo(b, N(b), 4) == 10);
    /* LRU e otimo nao sofrem a anomalia */
    assert(subst_lru(b, N(b), 3) == 10);
    assert(subst_lru(b, N(b), 4) == 8);
    assert(subst_otimo(b, N(b), 3) == 7);
    assert(subst_otimo(b, N(b), 4) == 6);

    /* bordas: cadeia vazia, 1 quadro, quadros >= paginas distintas */
    assert(subst_fifo(a, 0, 3) == 0 && subst_lru(a, 0, 3) == 0);
    assert(subst_clock(a, 0, 3) == 0 && subst_otimo(a, 0, 3) == 0);
    int c[] = {1, 2, 1, 2, 3, 3, 1};
    assert(subst_fifo(c, N(c), 1) == 6);   /* so o 3 repetido acerta */
    assert(subst_lru(c, N(c), 1) == 6);
    assert(subst_clock(c, N(c), 1) == 6);
    assert(subst_otimo(c, N(c), 1) == 6);
    assert(subst_fifo(c, N(c), 3) == 3 && subst_lru(c, N(c), 10) == 3);
    assert(subst_clock(c, N(c), 3) == 3 && subst_otimo(c, N(c), 3) == 3);
    assert(subst_fifo(c, N(c), 0) == -1 && subst_lru(c, N(c), 0) == -1);
    assert(subst_clock(c, N(c), 0) == -1 && subst_otimo(c, N(c), 0) == -1);

    /* repeticao da mesma pagina: 1 unica falta */
    int d[] = {4, 4, 4, 4};
    assert(subst_fifo(d, N(d), 2) == 1 && subst_clock(d, N(d), 2) == 1);

    /* propriedade: otimo <= qualquer outro */
    for (size_t q = 1; q <= 5; q++) {
        int o = subst_otimo(a, N(a), q);
        assert(o <= subst_fifo(a, N(a), q) && o <= subst_lru(a, N(a), q) &&
               o <= subst_clock(a, N(a), q));
    }

    puts("test_substituicao ok");
    return 0;
}
