#include <assert.h>

#include "pilha.h"

int main(void) {
    Pilha p;
    int v = 0;

    pilha_init(&p);
    assert(pilha_vazia(&p));
    assert(pilha_tamanho(&p) == 0);
    assert(!pilha_pop(&p, &v));
    assert(!pilha_topo(&p, &v));

    assert(pilha_push(&p, 10));
    assert(pilha_push(&p, 20));
    assert(pilha_push(&p, 30));
    assert(pilha_tamanho(&p) == 3);
    assert(pilha_topo(&p, &v) && v == 30);
    assert(pilha_tamanho(&p) == 3);

    assert(pilha_pop(&p, &v) && v == 30);
    assert(pilha_pop(&p, &v) && v == 20);
    assert(pilha_pop(&p, &v) && v == 10);
    assert(pilha_vazia(&p));

    for (int i = 0; i < PILHA_CAPACIDADE; i++) {
        assert(pilha_push(&p, i));
    }
    assert(pilha_cheia(&p));
    assert(!pilha_push(&p, 99));
    assert(pilha_pop(&p, &v) && v == PILHA_CAPACIDADE - 1);
    assert(!pilha_cheia(&p));
    return 0;
}
