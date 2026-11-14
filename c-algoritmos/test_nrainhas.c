#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include "nrainhas.h"

/* Valida que col descreve um posicionamento sem ataques. */
static int valida(int n, const int *col) {
    for (int i = 0; i < n; i++) {
        if (col[i] < 0 || col[i] >= n) return 0;
        for (int j = i + 1; j < n; j++)
            if (col[i] == col[j] || abs(col[i] - col[j]) == j - i) return 0;
    }
    return 1;
}

int main(void) {
    long esperado[] = {1, 1, 0, 0, 2, 10, 4, 40, 92, 352, 724};
    for (int n = 0; n <= 10; n++) assert(nrainhas_contar(n) == esperado[n]);
    assert(nrainhas_contar(12) == 14200);
    assert(nrainhas_contar(-1) == -1);
    assert(nrainhas_contar(17) == -1);

    int col[16];
    assert(nrainhas_primeira(2, col) == 0);
    assert(nrainhas_primeira(3, col) == 0);
    assert(nrainhas_primeira(1, col) == 1 && col[0] == 0);
    assert(nrainhas_primeira(0, col) == 1);
    assert(nrainhas_primeira(4, col) == 1 && valida(4, col));
    assert(col[0] == 1 && col[1] == 3 && col[2] == 0 && col[3] == 2);  /* lexicografica */
    assert(nrainhas_primeira(8, col) == 1 && valida(8, col));
    assert(col[0] == 0 && col[1] == 4 && col[2] == 7 && col[3] == 5);
    assert(nrainhas_primeira(16, col) == 1 && valida(16, col));
    assert(nrainhas_primeira(-3, col) == -1 && nrainhas_primeira(20, col) == -1);
    puts("nrainhas ok");
    return 0;
}
