#include <assert.h>
#include <stdio.h>
#include "fila_circular.h"

int main(void) {
    int x;
    assert(fila_nova(0) == NULL);
    Fila *f = fila_nova(3);
    assert(fila_vazia(f) && !fila_cheia(f));
    assert(!fila_desenfileirar(f, &x) && !fila_frente(f, &x));
    assert(fila_enfileirar(f, 1) && fila_enfileirar(f, 2) && fila_enfileirar(f, 3));
    assert(fila_cheia(f) && !fila_enfileirar(f, 4));
    assert(fila_desenfileirar(f, &x) && x == 1);
    assert(fila_enfileirar(f, 4));          /* da a volta no buffer */
    assert(fila_frente(f, &x) && x == 2);
    assert(fila_desenfileirar(f, &x) && x == 2);
    assert(fila_desenfileirar(f, &x) && x == 3);
    assert(fila_desenfileirar(f, &x) && x == 4);
    assert(fila_vazia(f) && fila_tam(f) == 0);
    for (int i = 0; i < 100; i++) {         /* muitas voltas */
        assert(fila_enfileirar(f, i));
        assert(fila_desenfileirar(f, &x) && x == i);
    }
    fila_liberar(f);
    Fila *um = fila_nova(1);
    assert(fila_enfileirar(um, 9) && fila_cheia(um) && !fila_enfileirar(um, 8));
    fila_liberar(um);
    fila_liberar(NULL);
    puts("fila_circular ok");
    return 0;
}
