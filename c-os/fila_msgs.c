#include "fila_msgs.h"

#include <stdlib.h>
#include <string.h>

struct FilaMsgs {
    Msg *buf;
    size_t cap;
    size_t ini; /* indice da mensagem mais antiga */
    size_t n;
};

FilaMsgs *fm_criar(size_t capacidade) {
    if (capacidade == 0) return NULL;
    FilaMsgs *f = calloc(1, sizeof *f);
    if (!f) return NULL;
    f->buf = calloc(capacidade, sizeof(Msg));
    if (!f->buf) {
        free(f);
        return NULL;
    }
    f->cap = capacidade;
    return f;
}

void fm_destruir(FilaMsgs *f) {
    if (!f) return;
    free(f->buf);
    free(f);
}

int fm_enviar(FilaMsgs *f, int remetente, int tipo, const void *dados, size_t tam) {
    if (tam > FM_MSG_MAX) return FM_GRANDE;
    if (f->n == f->cap) return FM_CHEIA;
    Msg *m = &f->buf[(f->ini + f->n) % f->cap];
    memset(m, 0, sizeof *m);
    m->remetente = remetente;
    m->tipo = tipo;
    m->tam = tam;
    if (tam) memcpy(m->dados, dados, tam);
    f->n++;
    return FM_OK;
}

int fm_espiar(const FilaMsgs *f, Msg *saida) {
    if (f->n == 0) return FM_VAZIA;
    *saida = f->buf[f->ini];
    return FM_OK;
}

int fm_receber(FilaMsgs *f, Msg *saida) {
    if (fm_espiar(f, saida) != FM_OK) return FM_VAZIA;
    f->ini = (f->ini + 1) % f->cap;
    f->n--;
    return FM_OK;
}

int fm_receber_tipo(FilaMsgs *f, int tipo, Msg *saida) {
    size_t k = 0;
    while (k < f->n && f->buf[(f->ini + k) % f->cap].tipo != tipo) k++;
    if (k == f->n) return FM_VAZIA;
    *saida = f->buf[(f->ini + k) % f->cap];
    /* fecha o buraco deslocando as mensagens seguintes uma posicao */
    for (size_t i = k; i + 1 < f->n; i++)
        f->buf[(f->ini + i) % f->cap] = f->buf[(f->ini + i + 1) % f->cap];
    f->n--;
    return FM_OK;
}

size_t fm_tamanho(const FilaMsgs *f) { return f->n; }
int fm_vazia(const FilaMsgs *f) { return f->n == 0; }
int fm_cheia(const FilaMsgs *f) { return f->n == f->cap; }
