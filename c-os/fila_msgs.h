#ifndef FILA_MSGS_H
#define FILA_MSGS_H

#include <stddef.h>

/* Fila de mensagens entre processos (IPC) sobre um buffer circular de
 * capacidade fixa, no estilo das filas de mensagens System V. */

#define FM_MSG_MAX 32

typedef struct {
    int remetente;
    int tipo;
    size_t tam;
    unsigned char dados[FM_MSG_MAX];
} Msg;

enum { FM_OK = 0, FM_CHEIA = -1, FM_VAZIA = -1, FM_GRANDE = -2 };

typedef struct FilaMsgs FilaMsgs;

FilaMsgs *fm_criar(size_t capacidade);
void fm_destruir(FilaMsgs *f);

/* FM_OK, FM_CHEIA ou FM_GRANDE (tam > FM_MSG_MAX). */
int fm_enviar(FilaMsgs *f, int remetente, int tipo, const void *dados, size_t tam);
/* Recebe a mensagem mais antiga. FM_OK ou FM_VAZIA. */
int fm_receber(FilaMsgs *f, Msg *saida);
/* Recebe a mais antiga com o `tipo` dado, preservando a ordem das demais. */
int fm_receber_tipo(FilaMsgs *f, int tipo, Msg *saida);
/* Le a proxima sem remover. */
int fm_espiar(const FilaMsgs *f, Msg *saida);

size_t fm_tamanho(const FilaMsgs *f);
int fm_vazia(const FilaMsgs *f);
int fm_cheia(const FilaMsgs *f);

#endif
