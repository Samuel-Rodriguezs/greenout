#include <assert.h>
#include <stdio.h>

#include "paginacao.h"

int main(void) {
    Paginacao *p = pag_criar();
    assert(p && pag_tabelas_alocadas(p) == 0);
    uint32_t fis = 0;

    /* sem mapeamento: falta de pagina */
    assert(pag_traduzir(p, 0x1000, 0, &fis) == PAG_FALTA);

    /* 0x00403004 = dir 1, tabela 3, offset 4 -> vpn 0x403 */
    assert(pag_mapear(p, 0x403, 0x7, 1) == 0);
    assert(pag_tabelas_alocadas(p) == 1);
    assert(pag_traduzir(p, 0x00403004, 0, &fis) == PAG_OK);
    assert(fis == 0x7004);
    assert(pag_acessado(p, 0x403) && !pag_sujo(p, 0x403));

    /* escrita marca sujo */
    assert(pag_traduzir(p, 0x00403FFF, 1, &fis) == PAG_OK && fis == 0x7FFF);
    assert(pag_sujo(p, 0x403));

    /* pagina vizinha na mesma tabela nao mapeada */
    assert(pag_traduzir(p, 0x00404000, 0, &fis) == PAG_FALTA);

    /* somente leitura: escrita gera protecao e nao marca sujo */
    assert(pag_mapear(p, 0x404, 0x9, 0) == 0);
    assert(pag_tabelas_alocadas(p) == 1); /* mesma tabela de 2o nivel */
    assert(pag_traduzir(p, 0x00404010, 0, &fis) == PAG_OK && fis == 0x9010);
    assert(pag_traduzir(p, 0x00404010, 1, &fis) == PAG_PROTECAO);
    assert(!pag_sujo(p, 0x404));

    /* outro diretorio: segunda tabela; ultimo endereco do espaco virtual */
    assert(pag_mapear(p, 0xFFFFF, 0xFFFFF, 1) == 0);
    assert(pag_tabelas_alocadas(p) == 2);
    assert(pag_traduzir(p, 0xFFFFFFFFu, 0, &fis) == PAG_OK && fis == 0xFFFFFFFFu);

    /* remapear sobrescreve */
    assert(pag_mapear(p, 0x403, 0x2, 1) == 0);
    assert(pag_traduzir(p, 0x00403004, 0, &fis) == PAG_OK && fis == 0x2004);

    /* desmapear libera tabela vazia */
    assert(pag_desmapear(p, 0xFFFFF) == 0);
    assert(pag_tabelas_alocadas(p) == 1);
    assert(pag_desmapear(p, 0xFFFFF) == -1);
    assert(pag_traduzir(p, 0xFFFFF000u, 0, &fis) == PAG_FALTA);
    assert(pag_desmapear(p, 0x403) == 0 && pag_tabelas_alocadas(p) == 1);
    assert(pag_desmapear(p, 0x404) == 0 && pag_tabelas_alocadas(p) == 0);

    /* limites de vpn/quadro */
    assert(pag_mapear(p, 0x100000, 1, 0) == -1);
    assert(pag_mapear(p, 1, 0x100000, 0) == -1);
    assert(pag_desmapear(p, 0x100000) == -1);
    pag_destruir(p);
    pag_destruir(NULL);

    puts("test_paginacao ok");
    return 0;
}
