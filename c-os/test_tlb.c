#include <assert.h>
#include <stdio.h>

#include "tlb.h"

int main(void) {
    assert(tlb_criar(0) == NULL);
    Tlb *t = tlb_criar(2);
    uint32_t q = 0;
    assert(t && tlb_tamanho(t) == 0);

    assert(!tlb_buscar(t, 1, &q));
    tlb_inserir(t, 1, 10);
    tlb_inserir(t, 2, 20);
    assert(tlb_tamanho(t) == 2);

    /* acessar 1 deixa 2 como LRU; inserir 3 despeja 2 */
    assert(tlb_buscar(t, 1, &q) && q == 10);
    tlb_inserir(t, 3, 30);
    assert(!tlb_buscar(t, 2, &q));
    assert(tlb_buscar(t, 1, &q) && q == 10);
    assert(tlb_buscar(t, 3, &q) && q == 30);

    /* contagem: faltas = 1 (inicial) + 1 (vpn 2); acertos = 3 */
    assert(tlb_faltas(t) == 2 && tlb_acertos(t) == 3);

    /* atualizar vpn existente nao despeja ninguem */
    tlb_inserir(t, 1, 11);
    assert(tlb_tamanho(t) == 2);
    assert(tlb_buscar(t, 1, &q) && q == 11);
    assert(tlb_buscar(t, 3, &q) && q == 30);

    /* invalidar abre vaga reaproveitada sem despejo */
    assert(tlb_invalidar(t, 3) == 1 && tlb_invalidar(t, 3) == 0);
    assert(tlb_tamanho(t) == 1);
    tlb_inserir(t, 4, 40);
    assert(tlb_buscar(t, 1, &q) && tlb_buscar(t, 4, &q) && q == 40);

    /* flush */
    tlb_limpar(t);
    assert(tlb_tamanho(t) == 0 && !tlb_buscar(t, 1, &q));
    tlb_destruir(t);

    /* padrao ciclico 1,2,3 com 2 entradas: LRU nunca acerta (thrashing) */
    t = tlb_criar(2);
    for (int r = 0; r < 3; r++)
        for (uint32_t v = 1; v <= 3; v++)
            if (!tlb_buscar(t, v, &q)) tlb_inserir(t, v, v * 10);
    assert(tlb_acertos(t) == 0 && tlb_faltas(t) == 9);
    tlb_destruir(t);

    /* capacidade 1 */
    t = tlb_criar(1);
    tlb_inserir(t, 5, 50);
    tlb_inserir(t, 6, 60);
    assert(!tlb_buscar(t, 5, &q) && tlb_buscar(t, 6, &q) && q == 60);
    tlb_destruir(t);
    tlb_destruir(NULL);

    puts("test_tlb ok");
    return 0;
}
