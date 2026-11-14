#include "rng.h"
#include <stdlib.h>

void xs_seed(Xorshift *r, uint64_t seed) {
    r->s = seed ? seed : 0x9E3779B97F4A7C15ULL; /* estado nao pode ser 0 */
}

uint64_t xs_next(Xorshift *r) {
    uint64_t x = r->s;
    x ^= x >> 12;
    x ^= x << 25;
    x ^= x >> 27;
    r->s = x;
    return x * 0x2545F4914F6CDD1DULL;
}

uint32_t pcg_next(Pcg32 *r) {
    uint64_t antigo = r->estado;
    r->estado = antigo * 6364136223846793005ULL + r->inc;
    uint32_t xorshifted = (uint32_t)(((antigo >> 18u) ^ antigo) >> 27u);
    uint32_t rot = (uint32_t)(antigo >> 59u);
    return (xorshifted >> rot) | (xorshifted << ((0u - rot) & 31u));
}

void pcg_seed(Pcg32 *r, uint64_t seed, uint64_t seq) {
    r->estado = 0;
    r->inc = (seq << 1u) | 1u;
    pcg_next(r);
    r->estado += seed;
    pcg_next(r);
}

double pcg_double(Pcg32 *r) { return pcg_next(r) / 4294967296.0; }

uint32_t pcg_limitado(Pcg32 *r, uint32_t limite) {
    /* Rejeita valores abaixo do limiar para evitar vies de modulo. */
    uint32_t limiar = (0u - limite) % limite;
    for (;;) {
        uint32_t v = pcg_next(r);
        if (v >= limiar) return v % limite;
    }
}

double rng_qui_quadrado(Pcg32 *r, uint32_t k, uint32_t n) {
    uint32_t *c = calloc(k, sizeof *c);
    if (!c) return -1;
    for (uint32_t i = 0; i < n; i++) c[pcg_limitado(r, k)]++;
    double esperado = (double)n / k, chi = 0;
    for (uint32_t i = 0; i < k; i++) {
        double d = c[i] - esperado;
        chi += d * d / esperado;
    }
    free(c);
    return chi;
}

double rng_media(Pcg32 *r, uint32_t n) {
    double soma = 0;
    for (uint32_t i = 0; i < n; i++) soma += pcg_double(r);
    return soma / n;
}
