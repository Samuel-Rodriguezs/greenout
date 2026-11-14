#include "fisher_yates.h"

#define SEED_PADRAO 2463534242u

void xorshift_iniciar(Xorshift *g, uint32_t seed) {
    g->estado = seed ? seed : SEED_PADRAO;
}

uint32_t xorshift_proximo(Xorshift *g) {
    uint32_t x = g->estado;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    g->estado = x;
    return x;
}

uint32_t xorshift_ate(Xorshift *g, uint32_t limite) {
    if (limite == 0) return 0;
    /* descarta a faixa final incompleta para manter a uniformidade */
    uint32_t zona = UINT32_MAX - (UINT32_MAX % limite);
    uint32_t r;
    do { r = xorshift_proximo(g); } while (r >= zona);
    return r % limite;
}

void embaralhar(int *a, size_t n, Xorshift *g) {
    for (size_t i = n; i > 1; i--) {
        size_t j = xorshift_ate(g, (uint32_t)i);   /* 0..i-1 */
        int t = a[i - 1]; a[i - 1] = a[j]; a[j] = t;
    }
}
