#include "busca.h"

size_t busca_limite_inferior(const int *a, size_t n, int chave) {
    size_t lo = 0, hi = n;
    while (lo < hi) {
        size_t m = lo + (hi - lo) / 2;
        if (a[m] < chave) lo = m + 1; else hi = m;
    }
    return lo;
}

long busca_binaria(const int *a, size_t n, int chave) {
    size_t i = busca_limite_inferior(a, n, chave);
    return (i < n && a[i] == chave) ? (long)i : -1;
}

long busca_interpolacao(const int *a, size_t n, int chave) {
    if (n == 0) return -1;
    size_t lo = 0, hi = n - 1;
    while (lo <= hi && chave >= a[lo] && chave <= a[hi]) {
        if (a[lo] == a[hi]) return (a[lo] == chave) ? (long)lo : -1;
        /* estimativa linear da posicao; long long evita overflow */
        long long num = (long long)chave - a[lo];
        long long den = (long long)a[hi] - a[lo];
        size_t pos = lo + (size_t)((long double)num * (long double)(hi - lo) / (long double)den);
        if (pos > hi) pos = hi;
        if (a[pos] == chave) return (long)pos;
        if (a[pos] < chave) lo = pos + 1;
        else {
            if (pos == 0) break;
            hi = pos - 1;
        }
    }
    return -1;
}
