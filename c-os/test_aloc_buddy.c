#include <assert.h>
#include <stdio.h>

#include "aloc_buddy.h"

int main(void) {
    /* memoria de 1024 = 64 * 2^4 */
    Buddy *b = buddy_criar(64, 4);
    assert(b);
    assert(buddy_livre_total(b) == 1024 && buddy_maior_livre(b) == 1024);
    assert(buddy_tamanho_reservado(b, 1) == 64);
    assert(buddy_tamanho_reservado(b, 65) == 128);
    assert(buddy_tamanho_reservado(b, 1025) == 0);

    /* cenario de livro-texto: pedidos 100 (->128), 240 (->256), 64 */
    long a = buddy_alocar(b, 100);
    long c = buddy_alocar(b, 240);
    long d = buddy_alocar(b, 64);
    assert(a == 0);      /* 128 em [0,128) */
    assert(d == 128);    /* 64 em [128,192) */
    assert(c == 256);    /* 256 em [256,512) */
    assert(buddy_livre_total(b) == 1024 - 128 - 256 - 64);
    assert(buddy_livres_na_ordem(b, 0) == 1);  /* [192,256) */
    assert(buddy_livres_na_ordem(b, 3) == 1);  /* [512,1024) */
    assert(buddy_maior_livre(b) == 512);

    /* liberar d funde com [192,256) e depois com a? a ocupa [0,128): para em 128 */
    assert(buddy_liberar(b, d) == 0);
    assert(buddy_livres_na_ordem(b, 0) == 0);
    assert(buddy_livres_na_ordem(b, 1) == 1);  /* [128,256) */
    assert(buddy_liberar(b, d) == -1);         /* duplo free */
    assert(buddy_liberar(b, 5) == -1);         /* nao alinhado */
    assert(buddy_liberar(b, 4096) == -1);      /* fora */

    /* liberando tudo, volta a um unico bloco de 1024 */
    assert(buddy_liberar(b, a) == 0);
    assert(buddy_liberar(b, c) == 0);
    assert(buddy_maior_livre(b) == 1024 && buddy_livres_na_ordem(b, 4) == 1);

    /* esgotamento: 16 blocos minimos, depois falha */
    long off[16];
    for (int i = 0; i < 16; i++) {
        off[i] = buddy_alocar(b, 64);
        assert(off[i] == i * 64);
    }
    assert(buddy_alocar(b, 1) == -1 && buddy_livre_total(b) == 0);
    for (int i = 15; i >= 0; i--) assert(buddy_liberar(b, off[i]) == 0);
    assert(buddy_maior_livre(b) == 1024);

    /* bordas */
    assert(buddy_alocar(b, 0) == -1);
    assert(buddy_alocar(b, 1025) == -1);
    assert(buddy_alocar(b, 1024) == 0);
    assert(buddy_criar(0, 3) == NULL);
    buddy_destruir(b);

    Buddy *u = buddy_criar(8, 0); /* um unico bloco */
    assert(buddy_alocar(u, 8) == 0 && buddy_alocar(u, 1) == -1);
    buddy_destruir(u);
    buddy_destruir(NULL);

    puts("test_aloc_buddy ok");
    return 0;
}
