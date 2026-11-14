#include "radixsort.h"
#include <stdlib.h>
#include <string.h>

int radixsort_u32(uint32_t *a, size_t n) {
    if (n < 2) return 0;
    uint32_t *buf = malloc(n * sizeof *buf);
    if (!buf) return -1;
    uint32_t *orig = a, *src = a, *dst = buf;
    for (int pass = 0; pass < 4; pass++) {
        int shift = pass * 8;
        size_t cont[257];
        memset(cont, 0, sizeof cont);
        for (size_t i = 0; i < n; i++) cont[((src[i] >> shift) & 0xFF) + 1]++;
        for (int d = 0; d < 256; d++) cont[d + 1] += cont[d];
        for (size_t i = 0; i < n; i++) dst[cont[(src[i] >> shift) & 0xFF]++] = src[i];
        uint32_t *t = src; src = dst; dst = t;
    }
    /* 4 passadas (par): resultado final volta em orig */
    if (src != orig) memcpy(orig, src, n * sizeof *orig);
    free(buf);
    return 0;
}
