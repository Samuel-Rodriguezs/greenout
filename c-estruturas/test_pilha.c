#include <assert.h>
#include <stdio.h>
#include "pilha.h"

int main(void) {
    Pilha *p = pilha_nova();
    int x;
    assert(pilha_vazia(p) && pilha_tam(p) == 0);
    assert(!pilha_desempilhar(p, &x));
    assert(!pilha_topo(p, &x));
    for (int i = 1; i <= 100; i++) assert(pilha_empilhar(p, i));
    assert(pilha_tam(p) == 100 && !pilha_vazia(p));
    assert(pilha_topo(p, &x) && x == 100);
    for (int i = 100; i > 50; i--) assert(pilha_desempilhar(p, &x) && x == i);
    assert(pilha_tam(p) == 50);
    pilha_liberar(p); /* libera com elementos */
    p = pilha_nova();
    assert(pilha_empilhar(p, 1) && pilha_desempilhar(p, NULL) && pilha_vazia(p));
    pilha_liberar(p);
    pilha_liberar(NULL);
    puts("pilha ok");
    return 0;
}
