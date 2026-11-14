#include <assert.h>
#include <stdio.h>
#include "avl.h"

int main(void) {
    Avl *a = avl_nova();
    int out[2048];
    assert(avl_tam(a) == 0 && avl_altura(a) == 0 && avl_valida(a));
    assert(!avl_buscar(a, 1) && !avl_remover(a, 1));

    /* insercao ordenada crescente: sem balanceamento daria altura 1000 */
    for (int i = 0; i < 1000; i++) {
        assert(avl_inserir(a, i));
        assert(avl_valida(a));
    }
    assert(!avl_inserir(a, 500));
    assert(avl_tam(a) == 1000);
    assert(avl_altura(a) <= 11);               /* ~1.44*log2(n) */
    assert(avl_buscar(a, 0) && avl_buscar(a, 999) && !avl_buscar(a, 1000));
    assert(avl_em_ordem(a, out, 2048) == 1000);
    for (int i = 0; i < 1000; i++) assert(out[i] == i);

    /* remocoes (inclusive raiz) mantendo a invariante */
    for (int i = 0; i < 1000; i += 3) {
        assert(avl_remover(a, i));
        assert(avl_valida(a));
    }
    assert(!avl_remover(a, 0));
    assert(avl_tam(a) == 666);
    avl_liberar(a);

    /* insercao decrescente e rotacoes duplas */
    a = avl_nova();
    for (int i = 100; i > 0; i--) assert(avl_inserir(a, i));
    assert(avl_valida(a) && avl_altura(a) <= 8);
    avl_liberar(a);
    a = avl_nova();
    assert(avl_inserir(a, 10) && avl_inserir(a, 30) && avl_inserir(a, 20)); /* RL */
    assert(a->raiz->chave == 20 && avl_valida(a));
    assert(avl_inserir(a, 5) && avl_inserir(a, 1) && avl_valida(a));
    while (avl_tam(a) > 0) assert(avl_remover(a, a->raiz->chave) && avl_valida(a));
    avl_liberar(a);
    avl_liberar(NULL);
    puts("avl ok");
    return 0;
}
