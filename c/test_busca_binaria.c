#include <assert.h>

#include "busca_binaria.h"

int main(void) {
    int v[] = {-5, 0, 3, 8, 12, 20, 21};
    size_t n = sizeof v / sizeof v[0];

    for (size_t i = 0; i < n; i++) {
        assert(busca_binaria(v, n, v[i]) == (long)i);
    }
    assert(busca_binaria(v, n, 4) == -1);
    assert(busca_binaria(v, n, -100) == -1);
    assert(busca_binaria(v, n, 100) == -1);

    assert(busca_binaria(v, 0, 3) == -1);
    int um[] = {7};
    assert(busca_binaria(um, 1, 7) == 0);
    assert(busca_binaria(um, 1, 8) == -1);
    return 0;
}
