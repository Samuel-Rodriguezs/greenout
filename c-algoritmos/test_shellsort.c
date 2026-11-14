#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include "shellsort.h"

int main(void) {
    shellsort(NULL, 0);
    int um[] = {5}; shellsort(um, 1); assert(um[0] == 5);
    int dois[] = {2, 1}; shellsort(dois, 2); assert(dois[0] == 1);
    int tres[] = {3, 2, 1}; shellsort(tres, 3);
    assert(tres[0] == 1 && tres[1] == 2 && tres[2] == 3);

    size_t tams[] = {10, 100, 702, 5000};
    for (int t = 0; t < 4; t++) {
        size_t n = tams[t];
        int *a = malloc(n * sizeof *a);
        assert(a);
        unsigned s = 31;
        for (size_t i = 0; i < n; i++) { s = s * 1103515245u + 12345u; a[i] = (int)(s >> 12) - 100000; }
        shellsort(a, n);
        for (size_t i = 1; i < n; i++) assert(a[i - 1] <= a[i]);
        for (size_t i = 0; i < n; i++) a[i] = (int)(n - i);
        shellsort(a, n);
        for (size_t i = 1; i < n; i++) assert(a[i - 1] <= a[i]);
        free(a);
    }
    puts("shellsort ok");
    return 0;
}
