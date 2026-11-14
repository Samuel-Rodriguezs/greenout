#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include "heapsort.h"

int main(void) {
    heapsort_int(NULL, 0);
    int um[] = {1}; heapsort_int(um, 1); assert(um[0] == 1);
    int dois[] = {9, -9}; heapsort_int(dois, 2); assert(dois[0] == -9 && dois[1] == 9);
    int c[] = {3, 1, 2}; heapsort_int(c, 3);
    assert(c[0] == 1 && c[1] == 2 && c[2] == 3);

    enum { N = 3000 };
    int *a = malloc(N * sizeof *a);
    assert(a);
    unsigned s = 7;
    for (int i = 0; i < N; i++) { s = s * 22695477u + 1u; a[i] = (int)(s >> 10) % 1000 - 500; }
    heapsort_int(a, N);
    for (int i = 1; i < N; i++) assert(a[i - 1] <= a[i]);
    heapsort_int(a, N);                         /* idempotente em ordenado */
    for (int i = 1; i < N; i++) assert(a[i - 1] <= a[i]);
    free(a);
    int ext[] = {2147483647, -2147483647 - 1, 0};
    heapsort_int(ext, 3);
    assert(ext[0] < ext[1] && ext[1] < ext[2]);
    puts("heapsort ok");
    return 0;
}
