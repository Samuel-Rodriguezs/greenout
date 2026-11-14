#include <assert.h>
#include <stdio.h>
#include <string.h>

#include "aloc_slab.h"

int main(void) {
    assert(slab_criar(0, 4) == NULL && slab_criar(8, 0) == NULL);
    SlabCache *c = slab_criar(16, 4);
    assert(c && slab_num_slabs(c) == 0 && slab_em_uso(c) == 0);

    /* 4 objetos cabem em um slab; o quinto cria o segundo */
    void *o[9];
    for (int i = 0; i < 4; i++) o[i] = slab_alocar(c);
    assert(slab_num_slabs(c) == 1 && slab_em_uso(c) == 4);
    o[4] = slab_alocar(c);
    assert(slab_num_slabs(c) == 2 && slab_em_uso(c) == 5);

    /* objetos distintos, zerados e utilizaveis */
    for (int i = 0; i < 5; i++)
        for (int j = i + 1; j < 5; j++) assert(o[i] != o[j]);
    for (int i = 0; i < 16; i++) assert(((unsigned char *)o[0])[i] == 0);
    memset(o[0], 0xAB, 16);
    assert(slab_liberar(c, o[0]) == 0);
    void *r = slab_alocar(c); /* reaproveita a vaga e vem zerado */
    assert(r == o[0] || slab_num_slabs(c) == 2);
    for (int i = 0; i < 16; i++) assert(((unsigned char *)r)[i] == 0);
    o[0] = r;

    /* erros: duplo free, ponteiro desalinhado, ponteiro alheio */
    assert(slab_liberar(c, o[1]) == 0);
    assert(slab_liberar(c, o[1]) == -1);
    assert(slab_liberar(c, (char *)o[2] + 1) == -1);
    int x;
    assert(slab_liberar(c, &x) == -1);
    assert(slab_liberar(c, NULL) == -1);
    assert(slab_em_uso(c) == 4);

    /* libera tudo e recolhe: slabs vazios voltam ao sistema */
    for (int i = 0; i < 5; i++)
        if (i != 1) assert(slab_liberar(c, o[i]) == 0);
    assert(slab_em_uso(c) == 0);
    assert(slab_recolher(c) == 2 && slab_num_slabs(c) == 0);
    assert(slab_recolher(c) == 0);

    /* depois de recolher, volta a alocar normalmente */
    assert(slab_alocar(c) != NULL && slab_num_slabs(c) == 1);

    /* slab de 1 objeto: cada alocacao cria um slab */
    SlabCache *u = slab_criar(1, 1);
    void *a = slab_alocar(u), *b = slab_alocar(u);
    assert(a != b && slab_num_slabs(u) == 2);
    slab_destruir(u); /* destroi com objetos em uso sem vazar */
    slab_destruir(c);
    slab_destruir(NULL);

    puts("test_aloc_slab ok");
    return 0;
}
