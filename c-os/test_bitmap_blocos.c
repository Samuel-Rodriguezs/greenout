#include <assert.h>
#include <stdio.h>

#include "bitmap_blocos.h"

int main(void) {
    assert(bb_criar(0) == NULL);
    BitmapBlocos *b = bb_criar(20); /* nao multiplo de 8 */
    assert(b && bb_livres(b) == 20 && bb_maior_extensao(b) == 20);

    /* alocacao simples: sempre o primeiro livre */
    assert(bb_alocar(b) == 0 && bb_alocar(b) == 1 && bb_alocar(b) == 2);
    assert(bb_ocupado(b, 1) && !bb_ocupado(b, 3) && bb_livres(b) == 17);

    /* liberar o 1 abre um buraco que e reutilizado */
    assert(bb_liberar(b, 1, 1) == 0);
    assert(bb_alocar(b) == 1);

    /* contiguo: blocos 3..7 */
    assert(bb_alocar_contiguo(b, 5) == 3);
    assert(bb_livres(b) == 12 && bb_maior_extensao(b) == 12);

    /* fragmentacao: libera 4..5 -> buraco de 2 entre ocupados */
    assert(bb_liberar(b, 4, 2) == 0);
    assert(bb_livres(b) == 14 && bb_maior_extensao(b) == 12);
    /* 3 contiguos nao cabem em [4,5]; vao para 8 */
    assert(bb_alocar_contiguo(b, 3) == 8);
    assert(bb_alocar_contiguo(b, 2) == 4); /* 2 cabem no buraco */
    assert(bb_maior_extensao(b) == 9);     /* 11..19 */

    /* liberacao invalida nao altera nada */
    assert(bb_liberar(b, 0, 0) == -1);
    assert(bb_liberar(b, 20, 1) == -1);
    assert(bb_liberar(b, 18, 3) == -1);  /* ultrapassa o fim */
    assert(bb_liberar(b, 7, 6) == -1);   /* inclui livres a partir do 11 */
    assert(bb_ocupado(b, 7) && bb_livres(b) == 9);

    /* esgotar e falhar */
    assert(bb_alocar_contiguo(b, 10) == -1);
    assert(bb_alocar_contiguo(b, 9) == 11);
    assert(bb_livres(b) == 0 && bb_alocar(b) == -1 && bb_maior_extensao(b) == 0);
    assert(bb_alocar_contiguo(b, 0) == -1);
    assert(bb_liberar(b, 0, 20) == 0);
    assert(bb_livres(b) == 20 && bb_maior_extensao(b) == 20);
    assert(bb_alocar_contiguo(b, 20) == 0);
    bb_destruir(b);
    bb_destruir(NULL);

    puts("test_bitmap_blocos ok");
    return 0;
}
