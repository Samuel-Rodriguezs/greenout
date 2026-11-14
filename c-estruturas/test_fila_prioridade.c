#include <assert.h>
#include <stdio.h>
#include "fila_prioridade.h"

int main(void) {
    Pq *q = pq_nova();
    int v, p;
    assert(pq_tam(q) == 0 && !pq_espiar(q, &v, &p) && !pq_remover(q, &v, &p));
    assert(pq_inserir(q, 10, 1) && pq_inserir(q, 20, 5) && pq_inserir(q, 30, 3));
    assert(pq_espiar(q, &v, &p) && v == 20 && p == 5);
    assert(pq_tam(q) == 3);
    assert(pq_remover(q, &v, &p) && v == 20);
    assert(pq_remover(q, &v, &p) && v == 30 && p == 3);
    assert(pq_remover(q, NULL, NULL));
    assert(pq_tam(q) == 0);

    /* estabilidade: mesma prioridade sai na ordem de insercao */
    for (int i = 0; i < 200; i++) assert(pq_inserir(q, i, 7));
    for (int i = 0; i < 200; i++) assert(pq_remover(q, &v, &p) && v == i && p == 7);

    /* prioridades negativas e extremas misturadas */
    assert(pq_inserir(q, 1, -5) && pq_inserir(q, 2, 0) && pq_inserir(q, 3, -5));
    assert(pq_inserir(q, 4, 2147483647) && pq_inserir(q, 5, -2147483647 - 1));
    int esperado[] = {4, 2, 1, 3, 5};
    for (int i = 0; i < 5; i++) assert(pq_remover(q, &v, &p) && v == esperado[i]);
    assert(!pq_remover(q, &v, &p));
    pq_liberar(q);
    pq_liberar(NULL);
    puts("fila_prioridade ok");
    return 0;
}
