#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include "radixsort.h"

int main(void) {
    assert(radixsort_u32(NULL, 0) == 0);
    uint32_t um[] = {42}; assert(radixsort_u32(um, 1) == 0 && um[0] == 42);
    uint32_t b[] = {4294967295u, 0, 256, 255, 65536, 1, 4294967295u};
    assert(radixsort_u32(b, 7) == 0);
    uint32_t esp[] = {0, 1, 255, 256, 65536, 4294967295u, 4294967295u};
    for (int i = 0; i < 7; i++) assert(b[i] == esp[i]);

    enum { N = 6000 };
    uint32_t *a = malloc(N * sizeof *a);
    assert(a);
    uint32_t s = 2463534242u;
    for (int i = 0; i < N; i++) { s ^= s << 13; s ^= s >> 17; s ^= s << 5; a[i] = s; }
    assert(radixsort_u32(a, N) == 0);
    for (int i = 1; i < N; i++) assert(a[i - 1] <= a[i]);
    free(a);
    puts("radixsort ok");
    return 0;
}
