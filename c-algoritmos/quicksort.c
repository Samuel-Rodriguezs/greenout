#include "quicksort.h"

#define LIMIAR_INSERCAO 12

static void trocar(int *x, int *y) { int t = *x; *x = *y; *y = t; }

static void insercao(int *a, size_t n) {
    for (size_t i = 1; i < n; i++) {
        int v = a[i];
        size_t j = i;
        while (j > 0 && a[j - 1] > v) { a[j] = a[j - 1]; j--; }
        a[j] = v;
    }
}

void quicksort(int *a, size_t n) {
    while (n > LIMIAR_INSERCAO) {
        /* mediana de tres colocada em a[n-1] como pivo */
        size_t m = n / 2;
        if (a[0] > a[m]) trocar(&a[0], &a[m]);
        if (a[0] > a[n - 1]) trocar(&a[0], &a[n - 1]);
        if (a[m] > a[n - 1]) trocar(&a[m], &a[n - 1]);
        trocar(&a[m], &a[n - 2]);
        int pivo = a[n - 2];
        size_t i = 0, j = n - 2;
        for (;;) {
            while (a[++i] < pivo) {}
            while (a[--j] > pivo) {}
            if (i >= j) break;
            trocar(&a[i], &a[j]);
        }
        trocar(&a[i], &a[n - 2]);
        /* recursao no menor lado, laco no maior */
        if (i < n - i - 1) {
            quicksort(a, i);
            a += i + 1;
            n -= i + 1;
        } else {
            quicksort(a + i + 1, n - i - 1);
            n = i;
        }
    }
    insercao(a, n);
}
