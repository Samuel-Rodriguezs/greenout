#include <assert.h>
#include <stdio.h>

#include "aloc_firstfit.h"

int main(void) {
    AlocFF *a = ff_criar(100);
    assert(a);
    assert(ff_livre_total(a) == 100 && ff_blocos_total(a) == 1);

    /* alocacoes sequenciais em first-fit */
    long x = ff_alocar(a, 30), y = ff_alocar(a, 20), z = ff_alocar(a, 40);
    assert(x == 0 && y == 30 && z == 50);
    assert(ff_livre_total(a) == 10 && ff_maior_livre(a) == 10);
    assert(ff_alocar(a, 11) == -1); /* nao cabe */

    /* libera o do meio: cria buraco de 20 */
    assert(ff_liberar(a, y) == 0);
    assert(ff_blocos_livres(a) == 2 && ff_maior_livre(a) == 20);
    assert(ff_liberar(a, y) == -1); /* duplo free */
    assert(ff_liberar(a, 7) == -1); /* endereco que nao inicia bloco */

    /* first-fit usa o primeiro buraco que serve (offset 30), nao o ultimo */
    long w = ff_alocar(a, 5);
    assert(w == 30);
    assert(ff_alocar(a, 15) == 35); /* resto do buraco: 15 */
    assert(ff_blocos_livres(a) == 1); /* sobrou so os 10 finais */

    /* coalescencia: libera tudo em ordem embaralhada */
    assert(ff_liberar(a, 0) == 0);
    assert(ff_liberar(a, 50) == 0);
    assert(ff_liberar(a, 35) == 0);
    assert(ff_liberar(a, 30) == 0);
    assert(ff_blocos_total(a) == 1 && ff_maior_livre(a) == 100);

    /* bordas */
    assert(ff_alocar(a, 0) == -1);
    assert(ff_alocar(a, 101) == -1);
    assert(ff_alocar(a, 100) == 0);
    assert(ff_livre_total(a) == 0 && ff_maior_livre(a) == 0);
    assert(ff_alocar(a, 1) == -1);
    assert(ff_liberar(a, 0) == 0);
    assert(ff_criar(0) == NULL);
    ff_destruir(a);
    ff_destruir(NULL);

    puts("test_aloc_firstfit ok");
    return 0;
}
