#include <assert.h>
#include <stdio.h>
#include "arvore_bst.h"

int main(void) {
    Bst *b = bst_nova();
    int x, out[16];
    assert(bst_tam(b) == 0 && bst_altura(b) == 0);
    assert(!bst_minimo(b, &x) && !bst_maximo(b, &x));
    assert(!bst_buscar(b, 1) && !bst_remover(b, 1));
    assert(bst_em_ordem(b, out, 16) == 0);
    int chaves[] = {50, 30, 70, 20, 40, 60, 80, 35, 45};
    for (size_t i = 0; i < 9; i++) assert(bst_inserir(b, chaves[i]));
    assert(!bst_inserir(b, 50));               /* duplicata */
    assert(bst_tam(b) == 9 && bst_altura(b) == 4);
    assert(bst_minimo(b, &x) && x == 20);
    assert(bst_maximo(b, &x) && x == 80);
    assert(bst_buscar(b, 45) && !bst_buscar(b, 46));
    assert(bst_em_ordem(b, out, 16) == 9);
    int ord[] = {20, 30, 35, 40, 45, 50, 60, 70, 80};
    for (size_t i = 0; i < 9; i++) assert(out[i] == ord[i]);
    assert(bst_em_ordem(b, out, 3) == 3 && out[2] == 35); /* buffer curto */
    assert(bst_remover(b, 20));                /* folha */
    assert(bst_remover(b, 70));                /* dois filhos */
    assert(bst_remover(b, 30));                /* dois filhos */
    assert(bst_remover(b, 50));                /* raiz */
    assert(!bst_remover(b, 50));
    assert(bst_tam(b) == 5);
    assert(bst_em_ordem(b, out, 16) == 5);
    int resto[] = {35, 40, 45, 60, 80};
    for (size_t i = 0; i < 5; i++) assert(out[i] == resto[i]);
    bst_liberar(b);

    /* degenerada: insercao ordenada */
    b = bst_nova();
    for (int i = 0; i < 100; i++) assert(bst_inserir(b, i));
    assert(bst_altura(b) == 100);
    for (int i = 0; i < 100; i++) assert(bst_remover(b, i));
    assert(bst_tam(b) == 0 && b->raiz == NULL);
    bst_liberar(b);
    bst_liberar(NULL);
    puts("arvore_bst ok");
    return 0;
}
