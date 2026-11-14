#include <assert.h>
#include <stdbool.h>
#include <stddef.h>

#include "lista_encadeada.h"

int main(void) {
    No *l = NULL;
    bool rem = false;

    assert(lista_tamanho(l) == 0);
    assert(!lista_contem(l, 1));

    l = lista_inserir_fim(l, 2);
    l = lista_inserir_fim(l, 3);
    l = lista_inserir_inicio(l, 1);
    assert(lista_tamanho(l) == 3);
    assert(l->valor == 1 && l->prox->valor == 2 && l->prox->prox->valor == 3);
    assert(lista_contem(l, 3));
    assert(!lista_contem(l, 4));

    l = lista_inverter(l);
    assert(l->valor == 3 && l->prox->valor == 2 && l->prox->prox->valor == 1);

    /* remove do meio, da cabeca, inexistente, e do fim */
    l = lista_remover(l, 2, &rem);
    assert(rem && lista_tamanho(l) == 2 && !lista_contem(l, 2));
    l = lista_remover(l, 3, &rem);
    assert(rem && l->valor == 1);
    l = lista_remover(l, 42, &rem);
    assert(!rem && lista_tamanho(l) == 1);
    l = lista_remover(l, 1, &rem);
    assert(rem && l == NULL);
    l = lista_remover(l, 1, NULL);
    assert(l == NULL);

    /* lista maior, liberada ao final (sem vazamento) */
    for (int i = 0; i < 1000; i++) {
        l = lista_inserir_inicio(l, i);
    }
    assert(lista_tamanho(l) == 1000);
    lista_liberar(l);
    lista_liberar(NULL);
    return 0;
}
