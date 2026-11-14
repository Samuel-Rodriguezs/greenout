#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include "quicksort.h"

static int ordenado(const int *a, size_t n) {
    for (size_t i = 1; i < n; i++) if (a[i - 1] > a[i]) return 0;
    return 1;
}

int main(void) {
    quicksort(NULL, 0);                       /* vazio */
    int um[] = {7}; quicksort(um, 1); assert(um[0] == 7);
    int dois[] = {2, 1}; quicksort(dois, 2); assert(dois[0] == 1 && dois[1] == 2);

    enum { N = 5000 };
    int *a = malloc(N * sizeof *a);
    assert(a);
    unsigned s = 12345;
    for (int caso = 0; caso < 5; caso++) {
        for (int i = 0; i < N; i++) {
            s = s * 1103515245u + 12345u;
            switch (caso) {
                case 0: a[i] = (int)(s >> 8) - (1 << 22); break; /* aleatorio c/ negativos */
                case 1: a[i] = i; break;                          /* ja ordenado */
                case 2: a[i] = N - i; break;                      /* inverso */
                case 3: a[i] = 5; break;                          /* todos iguais */
                default: a[i] = (int)((s >> 16) % 4); break;      /* muitos duplicados */
            }
        }
        quicksort(a, N);
        assert(ordenado(a, N));
    }
    free(a);
    int ext[] = {2147483647, -2147483647 - 1, 0, -1, 1};
    quicksort(ext, 5);
    assert(ordenado(ext, 5) && ext[0] == -2147483647 - 1);
    puts("quicksort ok");
    return 0;
}
