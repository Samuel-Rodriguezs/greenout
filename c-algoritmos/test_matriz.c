#include <assert.h>
#include <stdio.h>
#include "matriz.h"

static Matriz *de(size_t l, size_t c, const double *v) {
    Matriz *m = matriz_criar(l, c);
    assert(m);
    for (size_t i = 0; i < l; i++)
        for (size_t j = 0; j < c; j++) matriz_set(m, i, j, v[i * c + j]);
    return m;
}

int main(void) {
    assert(matriz_criar(0, 3) == NULL && matriz_criar(3, 0) == NULL);
    assert(matriz_criar((size_t)-1, 2) == NULL);          /* overflow tratado */
    matriz_liberar(NULL);

    double va[] = {1, 2, 3, 4, 5, 6};          /* 2x3 */
    double vb[] = {7, 8, 9, 10, 11, 12};       /* 3x2 */
    Matriz *a = de(2, 3, va), *b = de(3, 2, vb);
    Matriz *c = matriz_multiplicar(a, b);      /* 2x2 */
    assert(c && c->lin == 2 && c->col == 2);
    assert(matriz_get(c, 0, 0) == 58 && matriz_get(c, 0, 1) == 64);
    assert(matriz_get(c, 1, 0) == 139 && matriz_get(c, 1, 1) == 154);
    matriz_liberar(c);

    /* dimensoes incompativeis */
    assert(matriz_multiplicar(a, a) == NULL);

    /* identidade e elemento neutro */
    double vi[] = {1, 0, 0, 0, 1, 0, 0, 0, 1};
    Matriz *id = de(3, 3, vi);
    c = matriz_multiplicar(a, id);
    assert(c && c->lin == 2 && c->col == 3);
    for (size_t i = 0; i < 2; i++)
        for (size_t j = 0; j < 3; j++) assert(matriz_get(c, i, j) == matriz_get(a, i, j));
    matriz_liberar(c);

    /* transposta */
    Matriz *t = matriz_transposta(a);          /* 3x2 */
    assert(t && t->lin == 3 && t->col == 2);
    assert(matriz_get(t, 0, 1) == 4 && matriz_get(t, 2, 0) == 3 && matriz_get(t, 2, 1) == 6);
    Matriz *tt = matriz_transposta(t);
    assert(tt && tt->lin == 2 && tt->col == 3);
    for (size_t i = 0; i < 2; i++)
        for (size_t j = 0; j < 3; j++) assert(matriz_get(tt, i, j) == matriz_get(a, i, j));
    matriz_liberar(tt);
    matriz_liberar(t);

    /* 1x1 e vetor coluna x vetor linha */
    double v1[] = {5};
    Matriz *u = de(1, 1, v1);
    c = matriz_multiplicar(u, u);
    assert(c && matriz_get(c, 0, 0) == 25);
    matriz_liberar(c);
    matriz_liberar(u);
    double col3[] = {1, 2, 3}, lin3[] = {4, 5, 6};
    Matriz *vc = de(3, 1, col3), *vl = de(1, 3, lin3);
    c = matriz_multiplicar(vc, vl);            /* produto externo 3x3 */
    assert(c && c->lin == 3 && c->col == 3 && matriz_get(c, 2, 2) == 18);
    matriz_liberar(c);
    c = matriz_multiplicar(vl, vc);            /* produto interno 1x1 */
    assert(c && c->lin == 1 && c->col == 1 && matriz_get(c, 0, 0) == 32);
    matriz_liberar(c);
    matriz_liberar(vc); matriz_liberar(vl);
    matriz_liberar(id); matriz_liberar(a); matriz_liberar(b);
    puts("matriz ok");
    return 0;
}
