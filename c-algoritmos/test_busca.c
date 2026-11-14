#include <assert.h>
#include <stdio.h>
#include "busca.h"

int main(void) {
    int v[] = {-10, -3, 0, 2, 5, 9, 14, 100};
    size_t n = 8;
    for (size_t i = 0; i < n; i++) {
        assert(busca_binaria(v, n, v[i]) == (long)i);
        assert(busca_interpolacao(v, n, v[i]) == (long)i);
    }
    int ausentes[] = {-11, -4, 1, 10, 101, 2147483647, -2147483647 - 1};
    for (int i = 0; i < 7; i++) {
        assert(busca_binaria(v, n, ausentes[i]) == -1);
        assert(busca_interpolacao(v, n, ausentes[i]) == -1);
    }
    /* vazio e unitario */
    assert(busca_binaria(v, 0, 1) == -1 && busca_interpolacao(v, 0, 1) == -1);
    int u[] = {4};
    assert(busca_binaria(u, 1, 4) == 0 && busca_interpolacao(u, 1, 4) == 0);
    assert(busca_binaria(u, 1, 5) == -1 && busca_interpolacao(u, 1, 5) == -1);
    /* duplicados e todos iguais */
    int d[] = {1, 2, 2, 2, 3};
    long r = busca_binaria(d, 5, 2); assert(r >= 1 && r <= 3);
    r = busca_interpolacao(d, 5, 2); assert(r >= 1 && r <= 3);
    assert(busca_limite_inferior(d, 5, 2) == 1);
    assert(busca_limite_inferior(d, 5, 0) == 0);
    assert(busca_limite_inferior(d, 5, 9) == 5);
    int ig[] = {8, 8, 8};
    assert(busca_interpolacao(ig, 3, 8) >= 0 && busca_interpolacao(ig, 3, 7) == -1);
    /* extremos de int (testa overflow na estimativa) */
    int e[] = {-2147483647 - 1, 0, 2147483647};
    assert(busca_interpolacao(e, 3, 2147483647) == 2);
    assert(busca_interpolacao(e, 3, -2147483647 - 1) == 0);
    assert(busca_binaria(e, 3, 0) == 1);
    puts("busca ok");
    return 0;
}
