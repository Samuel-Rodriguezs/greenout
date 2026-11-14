#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "pool.h"

typedef struct { int id; char nome[20]; } Item;

int main(void) {
    Pool p;
    assert(pool_init(&p, sizeof(Item), 4) == 0);
    Item *it[4];
    for (int i = 0; i < 4; i++) {
        it[i] = pool_alloc(&p);
        assert(it[i]);
        it[i]->id = i;
        strcpy(it[i]->nome, "item");
    }
    assert(p.em_uso == 4);
    assert(pool_alloc(&p) == NULL); /* esgotado */

    /* Liberar e realocar reaproveita o mesmo bloco (LIFO). */
    Item *b = it[2];
    assert(pool_free(&p, b) == 0);
    assert(p.em_uso == 3);
    assert(pool_alloc(&p) == b);
    assert(it[0]->id == 0 && it[3]->id == 3);

    int fora;
    assert(pool_free(&p, &fora) == -1);
    assert(pool_free(&p, (char *)it[0] + 1) == -1);
    assert(pool_free(&p, NULL) == -1);

    pool_destruir(&p);
    assert(pool_init(&p, 8, 0) == -1);
    puts("pool ok");
    return 0;
}
