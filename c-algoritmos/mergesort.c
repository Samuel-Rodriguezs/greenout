#include "mergesort.h"
#include <stdlib.h>
#include <string.h>

static void ordenar(int *a, int *tmp, size_t n) {
    if (n < 2) return;
    size_t m = n / 2;
    ordenar(a, tmp, m);
    ordenar(a + m, tmp, n - m);
    size_t i = 0, j = m, k = 0;
    while (i < m && j < n) tmp[k++] = (a[j] < a[i]) ? a[j++] : a[i++];
    while (i < m) tmp[k++] = a[i++];
    while (j < n) tmp[k++] = a[j++];
    memcpy(a, tmp, n * sizeof *a);
}

int mergesort_int(int *a, size_t n) {
    if (n < 2) return 0;
    int *tmp = malloc(n * sizeof *tmp);
    if (!tmp) return -1;
    ordenar(a, tmp, n);
    free(tmp);
    return 0;
}
