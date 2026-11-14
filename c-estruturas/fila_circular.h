#ifndef FILA_CIRCULAR_H
#define FILA_CIRCULAR_H
#include <stdbool.h>
#include <stddef.h>

/* Fila FIFO de capacidade fixa sobre buffer circular. */
typedef struct {
    int *buf;
    size_t cap;
    size_t ini;   /* indice do primeiro elemento */
    size_t tam;
} Fila;

Fila *fila_nova(size_t capacidade);   /* capacidade 0 -> NULL */
void fila_liberar(Fila *f);
bool fila_enfileirar(Fila *f, int x); /* false se cheia */
bool fila_desenfileirar(Fila *f, int *saida);
bool fila_frente(const Fila *f, int *saida);
bool fila_vazia(const Fila *f);
bool fila_cheia(const Fila *f);
size_t fila_tam(const Fila *f);

#endif
