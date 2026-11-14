#include <assert.h>

#include "crivo.h"

int main(void) {
    unsigned p[32];

    assert(crivo_primos(0, p, 32) == 0);
    assert(crivo_primos(1, p, 32) == 0);

    assert(crivo_primos(2, p, 32) == 1);
    assert(p[0] == 2);

    size_t n = crivo_primos(30, p, 32);
    unsigned esperado[] = {2, 3, 5, 7, 11, 13, 17, 19, 23, 29};
    assert(n == 10);
    for (size_t i = 0; i < n; i++) {
        assert(p[i] == esperado[i]);
    }

    /* Capacidade menor: conta tudo, grava so o que cabe. */
    unsigned pequeno[3];
    assert(crivo_primos(30, pequeno, 3) == 10);
    assert(pequeno[0] == 2 && pequeno[1] == 3 && pequeno[2] == 5);

    /* So contagem. */
    assert(crivo_primos(100, NULL, 0) == 25);
    assert(crivo_primos(10000, NULL, 0) == 1229);
    return 0;
}
