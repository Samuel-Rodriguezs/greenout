#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include "mergesort.h"

int main(void) {
    assert(mergesort_int(NULL, 0) == 0);
    int um[] = {3}; assert(mergesort_int(um, 1) == 0 && um[0] == 3);
    int b[] = {5, -2, 9, 0, 5, 1, -7};
    assert(mergesort_int(b, 7) == 0);
    int esp[] = {-7, -2, 0, 1, 5, 5, 9};
    for (int i = 0; i < 7; i++) assert(b[i] == esp[i]);

    enum { N = 4001 };
    int *a = malloc(N * sizeof *a);
    assert(a);
    unsigned s = 99;
    for (int i = 0; i < N; i++) { s = s * 1664525u + 1013904223u; a[i] = (int)(s >> 20) - 2048; }
    assert(mergesort_int(a, N) == 0);
    for (int i = 1; i < N; i++) assert(a[i - 1] <= a[i]);
    for (int i = 0; i < N; i++) a[i] = N - i;       /* inverso */
    assert(mergesort_int(a, N) == 0);
    for (int i = 0; i < N; i++) assert(a[i] == i + 1);
    free(a);
    int iguais[] = {4, 4, 4, 4};
    assert(mergesort_int(iguais, 4) == 0 && iguais[3] == 4);
    puts("mergesort ok");
    return 0;
}
