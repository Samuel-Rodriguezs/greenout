#include "crivo.h"

#include <stdbool.h>
#include <stdlib.h>

size_t crivo_primos(unsigned limite, unsigned *saida, size_t cap) {
    if (limite < 2) {
        return 0;
    }
    bool *composto = calloc((size_t)limite + 1, sizeof *composto);
    if (composto == NULL) {
        return 0;
    }
    for (size_t i = 2; i * i <= limite; i++) {
        if (!composto[i]) {
            for (size_t j = i * i; j <= limite; j += i) {
                composto[j] = true;
            }
        }
    }
    size_t total = 0;
    for (size_t i = 2; i <= limite; i++) {
        if (!composto[i]) {
            if (saida != NULL && total < cap) {
                saida[total] = (unsigned)i;
            }
            total++;
        }
    }
    free(composto);
    return total;
}
