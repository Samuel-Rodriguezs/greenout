#include "countingsort.h"
#include <stdlib.h>

#define FAIXA_MAX 50000000LL

int countingsort(int *a, size_t n) {
    if (n < 2) return 0;
    int mn = a[0], mx = a[0];
    for (size_t i = 1; i < n; i++) {
        if (a[i] < mn) mn = a[i];
        if (a[i] > mx) mx = a[i];
    }
    long long faixa = (long long)mx - (long long)mn + 1;
    if (faixa > FAIXA_MAX) return -1;
    size_t *cont = calloc((size_t)faixa, sizeof *cont);
    if (!cont) return -1;
    for (size_t i = 0; i < n; i++) cont[(long long)a[i] - mn]++;
    size_t k = 0;
    for (long long v = 0; v < faixa; v++)
        for (size_t c = cont[v]; c > 0; c--) a[k++] = (int)(v + mn);
    free(cont);
    return 0;
}
