#include <assert.h>
#include <stdio.h>
#include <string.h>

#include "fila_msgs.h"

int main(void) {
    assert(fm_criar(0) == NULL);
    FilaMsgs *f = fm_criar(3);
    Msg m;
    assert(f && fm_vazia(f) && !fm_cheia(f));
    assert(fm_receber(f, &m) == FM_VAZIA && fm_espiar(f, &m) == FM_VAZIA);

    /* FIFO basico com payload */
    assert(fm_enviar(f, 10, 1, "ola", 4) == FM_OK);
    assert(fm_enviar(f, 11, 2, "mundo", 6) == FM_OK);
    assert(fm_tamanho(f) == 2);
    assert(fm_espiar(f, &m) == FM_OK && m.remetente == 10 && fm_tamanho(f) == 2);
    assert(fm_receber(f, &m) == FM_OK);
    assert(m.remetente == 10 && m.tipo == 1 && m.tam == 4 && strcmp((char *)m.dados, "ola") == 0);

    /* encher: capacidade 3 (ja ha 1) */
    assert(fm_enviar(f, 12, 1, "a", 1) == FM_OK);
    assert(fm_enviar(f, 13, 3, NULL, 0) == FM_OK); /* mensagem vazia */
    assert(fm_cheia(f));
    assert(fm_enviar(f, 14, 1, "x", 1) == FM_CHEIA);

    /* o buffer deu a volta: recebe por tipo do meio da fila */
    assert(fm_receber_tipo(f, 1, &m) == FM_OK && m.remetente == 12);
    assert(fm_receber_tipo(f, 9, &m) == FM_VAZIA); /* tipo inexistente */
    assert(fm_tamanho(f) == 2 && !fm_cheia(f));

    /* ordem preservada: 11 (tipo 2) depois 13 (tipo 3) */
    assert(fm_receber(f, &m) == FM_OK && m.remetente == 11 && strcmp((char *)m.dados, "mundo") == 0);
    assert(fm_receber(f, &m) == FM_OK && m.remetente == 13 && m.tam == 0);
    assert(fm_vazia(f));

    /* tamanho maximo e excesso */
    unsigned char grande[FM_MSG_MAX + 1] = {0};
    assert(fm_enviar(f, 1, 1, grande, FM_MSG_MAX) == FM_OK);
    assert(fm_enviar(f, 1, 1, grande, FM_MSG_MAX + 1) == FM_GRANDE);
    assert(fm_tamanho(f) == 1);

    /* varias voltas no buffer circular, mantendo a ordem */
    fm_receber(f, &m);
    for (int i = 0; i < 20; i++) {
        assert(fm_enviar(f, i, i % 2, &i, sizeof i) == FM_OK);
        assert(fm_receber(f, &m) == FM_OK && m.remetente == i);
    }
    /* receber por tipo no inicio/fim com o buffer deslocado */
    fm_enviar(f, 1, 5, "a", 1);
    fm_enviar(f, 2, 6, "b", 1);
    fm_enviar(f, 3, 5, "c", 1);
    assert(fm_receber_tipo(f, 5, &m) == FM_OK && m.remetente == 1);
    assert(fm_receber_tipo(f, 5, &m) == FM_OK && m.remetente == 3);
    assert(fm_receber(f, &m) == FM_OK && m.remetente == 2 && fm_vazia(f));
    fm_destruir(f);
    fm_destruir(NULL);

    puts("test_fila_msgs ok");
    return 0;
}
