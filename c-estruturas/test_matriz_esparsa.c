#include <assert.h>
#include <stdio.h>
#include "matriz_esparsa.h"

int main(void) {
    Matriz *m = matriz_nova(3, 4);
    assert(matriz_nnz(m) == 0 && matriz_obter(m, 1, 1) == 0.0);
    assert(!matriz_definir(m, 3, 0, 1.0) && !matriz_definir(m, 0, 4, 1.0));
    assert(matriz_obter(m, 9, 9) == 0.0);
    assert(matriz_definir(m, 0, 2, 5.0) && matriz_definir(m, 0, 0, 1.0));
    assert(matriz_definir(m, 2, 3, -2.5) && matriz_definir(m, 0, 1, 3.0));
    assert(matriz_nnz(m) == 4);
    assert(matriz_obter(m, 0, 0) == 1.0 && matriz_obter(m, 0, 1) == 3.0);
    assert(matriz_obter(m, 0, 2) == 5.0 && matriz_obter(m, 2, 3) == -2.5);
    assert(matriz_definir(m, 0, 1, 7.0) && matriz_nnz(m) == 4);   /* sobrescreve */
    assert(matriz_obter(m, 0, 1) == 7.0);
    assert(matriz_definir(m, 1, 1, 0.0) && matriz_nnz(m) == 4);   /* zero em ausente */
    assert(matriz_definir(m, 0, 1, 0.0) && matriz_nnz(m) == 3);   /* remove */
    assert(matriz_obter(m, 0, 1) == 0.0 && matriz_obter(m, 0, 2) == 5.0);

    Matriz *t = matriz_transposta(m);
    assert(t->linhas == 4 && t->colunas == 3 && matriz_nnz(t) == 3);
    assert(matriz_obter(t, 2, 0) == 5.0 && matriz_obter(t, 3, 2) == -2.5);

    Matriz *s = matriz_somar(m, m);
    assert(s && matriz_obter(s, 0, 2) == 10.0 && matriz_nnz(s) == 3);
    Matriz *neg = matriz_nova(3, 4);
    assert(matriz_definir(neg, 0, 2, -5.0) && matriz_definir(neg, 1, 0, 4.0));
    Matriz *s2 = matriz_somar(m, neg);              /* 5 + -5 cancela e some */
    assert(s2 && matriz_obter(s2, 0, 2) == 0.0 && matriz_nnz(s2) == 3);
    assert(matriz_obter(s2, 1, 0) == 4.0 && matriz_obter(s2, 0, 0) == 1.0);
    assert(matriz_somar(m, t) == NULL);             /* dimensoes diferentes */

    /* produto: m (3x4) * t (4x3) = 3x3 */
    Matriz *p = matriz_multiplicar(m, t);
    assert(p && p->linhas == 3 && p->colunas == 3);
    assert(matriz_obter(p, 0, 0) == 26.0);          /* 1*1 + 5*5 */
    assert(matriz_obter(p, 2, 2) == 6.25);
    assert(matriz_obter(p, 0, 2) == 0.0 && matriz_nnz(p) == 2);
    assert(matriz_multiplicar(m, m) == NULL);       /* 4 != 3 */

    Matriz *vazia = matriz_nova(0, 0);              /* degenerada */
    Matriz *pv = matriz_multiplicar(vazia, vazia);
    assert(pv && matriz_nnz(pv) == 0);
    matriz_liberar(pv);
    matriz_liberar(vazia);
    matriz_liberar(p);
    matriz_liberar(s2);
    matriz_liberar(neg);
    matriz_liberar(s);
    matriz_liberar(t);
    matriz_liberar(m);
    matriz_liberar(NULL);
    puts("matriz_esparsa ok");
    return 0;
}
