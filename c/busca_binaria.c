#include "busca_binaria.h"

long busca_binaria(const int *v, size_t n, int alvo) {
    size_t lo = 0, hi = n; /* intervalo [lo, hi) */
    while (lo < hi) {
        size_t meio = lo + (hi - lo) / 2;
        if (v[meio] == alvo) {
            return (long)meio;
        }
        if (v[meio] < alvo) {
            lo = meio + 1;
        } else {
            hi = meio;
        }
    }
    return -1;
}
