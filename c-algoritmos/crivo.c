#include "crivo.h"
#include <stdint.h>
#include <stdlib.h>

/* Bit i representa o numero 2*i+1 (so impares). Bit 1 = composto/nao primo. */
struct Crivo {
    size_t limite;
    size_t n_bits;
    uint64_t *bits;
};

static int bit_get(const uint64_t *b, size_t i) { return (int)((b[i >> 6] >> (i & 63)) & 1u); }
static void bit_set(uint64_t *b, size_t i) { b[i >> 6] |= (uint64_t)1 << (i & 63); }

Crivo *crivo_criar(size_t limite) {
    Crivo *c = malloc(sizeof *c);
    if (!c) return NULL;
    c->limite = limite;
    c->n_bits = limite / 2 + 1;          /* indices 0..limite/2 -> impares 1..2*(limite/2)+1 */
    c->bits = calloc((c->n_bits + 63) / 64, sizeof *c->bits);
    if (!c->bits) { free(c); return NULL; }
    bit_set(c->bits, 0);                 /* 1 nao e primo */
    for (size_t i = 1; ; i++) {
        size_t p = 2 * i + 1;
        if (p * p > limite) break;
        if (bit_get(c->bits, i)) continue;
        for (size_t m = p * p; m <= limite; m += 2 * p) bit_set(c->bits, m / 2);
    }
    return c;
}

void crivo_liberar(Crivo *c) {
    if (!c) return;
    free(c->bits);
    free(c);
}

int crivo_eh_primo(const Crivo *c, size_t n) {
    if (n > c->limite || n < 2) return 0;
    if (n == 2) return 1;
    if ((n & 1) == 0) return 0;
    return !bit_get(c->bits, n / 2);
}

size_t crivo_contar(const Crivo *c) {
    size_t total = 0;
    for (size_t n = 2; n <= c->limite; n++) total += (size_t)crivo_eh_primo(c, n);
    return total;
}
