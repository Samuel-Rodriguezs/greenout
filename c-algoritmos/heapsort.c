#include "heapsort.h"

/* Desce o elemento da posicao i num max-heap de tamanho n. */
static void peneirar(int *a, size_t i, size_t n) {
    int v = a[i];
    for (;;) {
        size_t f = 2 * i + 1;
        if (f >= n) break;
        if (f + 1 < n && a[f + 1] > a[f]) f++;
        if (a[f] <= v) break;
        a[i] = a[f];
        i = f;
    }
    a[i] = v;
}

void heapsort_int(int *a, size_t n) {
    if (n < 2) return;
    for (size_t i = n / 2; i-- > 0;) peneirar(a, i, n);
    for (size_t fim = n - 1; fim > 0; fim--) {
        int t = a[0]; a[0] = a[fim]; a[fim] = t;
        peneirar(a, 0, fim);
    }
}
