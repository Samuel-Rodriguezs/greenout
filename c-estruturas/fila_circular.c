#include "fila_circular.h"
#include <stdlib.h>

Fila *fila_nova(size_t capacidade) {
    if (capacidade == 0) return NULL;
    Fila *f = malloc(sizeof *f);
    if (!f) return NULL;
    f->buf = malloc(capacidade * sizeof(int));
    if (!f->buf) {
        free(f);
        return NULL;
    }
    f->cap = capacidade;
    f->ini = 0;
    f->tam = 0;
    return f;
}

void fila_liberar(Fila *f) {
    if (!f) return;
    free(f->buf);
    free(f);
}

bool fila_enfileirar(Fila *f, int x) {
    if (f->tam == f->cap) return false;
    f->buf[(f->ini + f->tam) % f->cap] = x;
    f->tam++;
    return true;
}

bool fila_desenfileirar(Fila *f, int *saida) {
    if (f->tam == 0) return false;
    if (saida) *saida = f->buf[f->ini];
    f->ini = (f->ini + 1) % f->cap;
    f->tam--;
    return true;
}

bool fila_frente(const Fila *f, int *saida) {
    if (f->tam == 0) return false;
    if (saida) *saida = f->buf[f->ini];
    return true;
}

bool fila_vazia(const Fila *f) { return f->tam == 0; }
bool fila_cheia(const Fila *f) { return f->tam == f->cap; }
size_t fila_tam(const Fila *f) { return f->tam; }
