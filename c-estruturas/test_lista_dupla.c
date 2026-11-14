#include <assert.h>
#include <stdio.h>
#include "lista_dupla.h"

int main(void) {
    Lista *l = lista_nova();
    int x;
    assert(!lista_pop_frente(l, &x) && !lista_pop_tras(l, &x));
    assert(!lista_remover_valor(l, 1));
    assert(lista_push_tras(l, 2) && lista_push_tras(l, 3) && lista_push_frente(l, 1));
    assert(lista_tam(l) == 3);
    assert(lista_obter(l, 0, &x) && x == 1);
    assert(lista_obter(l, 2, &x) && x == 3);
    assert(!lista_obter(l, 3, &x));
    assert(lista_inserir(l, 3, 5) && lista_inserir(l, 0, 0) && lista_inserir(l, 2, 99));
    assert(!lista_inserir(l, 100, 1));
    /* 0 1 99 2 3 5 */
    int esperado[] = {0, 1, 99, 2, 3, 5};
    for (size_t i = 0; i < 6; i++) assert(lista_obter(l, i, &x) && x == esperado[i]);
    assert(lista_remover_valor(l, 99) && lista_tam(l) == 5);
    assert(!lista_remover_valor(l, 99));
    lista_inverter(l);
    int inv[] = {5, 3, 2, 1, 0};
    for (size_t i = 0; i < 5; i++) assert(lista_obter(l, i, &x) && x == inv[i]);
    assert(lista_pop_frente(l, &x) && x == 5);
    assert(lista_pop_tras(l, &x) && x == 0);
    while (lista_pop_tras(l, &x)) {}
    assert(lista_tam(l) == 0 && l->cabeca == NULL && l->cauda == NULL);
    lista_inverter(l);
    assert(lista_push_frente(l, 7));
    lista_liberar(l); /* libera elemento restante */
    lista_liberar(NULL);
    puts("lista_dupla ok");
    return 0;
}
