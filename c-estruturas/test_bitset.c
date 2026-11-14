#include <assert.h>
#include <stdio.h>
#include "bitset.h"

int main(void) {
    Bitset *z = bitset_novo(0);                    /* vazio */
    assert(bitset_tamanho(z) == 0 && bitset_contar(z) == 0);
    assert(!bitset_definir(z, 0) && !bitset_testar(z, 0) && bitset_proximo(z, 0) == 0);
    bitset_inverter(z);
    bitset_liberar(z);

    Bitset *b = bitset_novo(130);                  /* atravessa 3 palavras */
    assert(bitset_tamanho(b) == 130 && bitset_contar(b) == 0);
    assert(bitset_definir(b, 0) && bitset_definir(b, 63) && bitset_definir(b, 64));
    assert(bitset_definir(b, 129));
    assert(!bitset_definir(b, 130) && !bitset_limpar(b, 500) && !bitset_alternar(b, 130));
    assert(bitset_testar(b, 63) && bitset_testar(b, 64) && !bitset_testar(b, 65));
    assert(!bitset_testar(b, 130));
    assert(bitset_contar(b) == 4);
    assert(bitset_proximo(b, 0) == 0 && bitset_proximo(b, 1) == 63);
    assert(bitset_proximo(b, 65) == 129 && bitset_proximo(b, 130) == 130);
    assert(bitset_limpar(b, 63) && !bitset_testar(b, 63) && bitset_contar(b) == 3);
    assert(bitset_alternar(b, 63) && bitset_testar(b, 63));
    assert(bitset_alternar(b, 63) && !bitset_testar(b, 63));

    bitset_inverter(b);                            /* complemento nao pode vazar alem de n */
    assert(bitset_contar(b) == 130 - 3);
    assert(!bitset_testar(b, 0) && bitset_testar(b, 1));
    bitset_inverter(b);

    Bitset *c = bitset_novo(130);
    assert(bitset_definir(c, 0) && bitset_definir(c, 5) && bitset_definir(c, 129));
    Bitset *u = bitset_novo(130);
    assert(bitset_ou(u, b) && bitset_ou(u, c) && bitset_contar(u) == 4); /* {0,5,64,129} */
    assert(bitset_e(u, c) && bitset_contar(u) == 3);                     /* {0,5,129} */
    assert(bitset_xor(u, b) && bitset_contar(u) == 2);                   /* {5,64} */
    assert(bitset_testar(u, 5) && bitset_testar(u, 64) && !bitset_testar(u, 0));
    Bitset *outro = bitset_novo(10);
    assert(!bitset_e(b, outro) && !bitset_ou(b, outro) && !bitset_xor(b, outro));
    bitset_liberar(outro);
    bitset_liberar(u);
    bitset_liberar(c);
    bitset_liberar(b);
    bitset_liberar(NULL);
    puts("bitset ok");
    return 0;
}
