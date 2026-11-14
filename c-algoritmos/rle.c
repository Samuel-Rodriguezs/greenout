#include "rle.h"
#include <stdlib.h>

uint8_t *rle_codificar(const uint8_t *entrada, size_t n, size_t *saida_n) {
    /* pior caso: cada byte vira um par -> 2n; aloca pelo menos 1 */
    uint8_t *out = malloc(2 * n + 1);
    if (!out) return NULL;
    size_t k = 0;
    for (size_t i = 0; i < n;) {
        size_t j = i;
        while (j < n && entrada[j] == entrada[i] && j - i < 255) j++;
        out[k++] = (uint8_t)(j - i);
        out[k++] = entrada[i];
        i = j;
    }
    *saida_n = k;
    return out;
}

uint8_t *rle_decodificar(const uint8_t *entrada, size_t n, size_t *saida_n) {
    if (n % 2 != 0) return NULL;
    size_t total = 0;
    for (size_t i = 0; i < n; i += 2) {
        if (entrada[i] == 0) return NULL;
        total += entrada[i];
    }
    uint8_t *out = malloc(total + 1);
    if (!out) return NULL;
    size_t k = 0;
    for (size_t i = 0; i < n; i += 2)
        for (unsigned c = entrada[i]; c > 0; c--) out[k++] = entrada[i + 1];
    *saida_n = k;
    return out;
}
