#include "mochila.h"
#include <stdlib.h>

long mochila(const int *peso, const int *valor, size_t n, int cap) {
    if (cap < 0) return -1;
    for (size_t i = 0; i < n; i++)
        if (peso[i] <= 0 || valor[i] < 0) return -1;
    long *dp = calloc((size_t)cap + 1, sizeof *dp);
    if (!dp) return -1;
    for (size_t i = 0; i < n; i++) {
        /* percorre capacidade em ordem decrescente: cada item usado uma vez */
        for (int c = cap; c >= peso[i]; c--) {
            long cand = dp[c - peso[i]] + valor[i];
            if (cand > dp[c]) dp[c] = cand;
        }
    }
    long r = dp[cap];
    free(dp);
    return r;
}
