#include "shellsort.h"

static const size_t CIURA[] = {1, 4, 10, 23, 57, 132, 301, 701};
#define N_CIURA (sizeof CIURA / sizeof CIURA[0])

void shellsort(int *a, size_t n) {
    /* acha a maior lacuna util, estendendo alem de 701 se preciso */
    size_t gaps[40];
    size_t ng = 0;
    for (size_t i = 0; i < N_CIURA && CIURA[i] < n; i++) gaps[ng++] = CIURA[i];
    if (ng == N_CIURA) {
        size_t g = CIURA[N_CIURA - 1];
        while (ng < 40) {
            g = g * 9 / 4;
            if (g >= n) break;
            gaps[ng++] = g;
        }
    }
    while (ng-- > 0) {
        size_t gap = gaps[ng];
        for (size_t i = gap; i < n; i++) {
            int v = a[i];
            size_t j = i;
            while (j >= gap && a[j - gap] > v) { a[j] = a[j - gap]; j -= gap; }
            a[j] = v;
        }
    }
}
