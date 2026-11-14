#ifndef PILHA_H
#define PILHA_H
#include <stdbool.h>
#include <stddef.h>

/* Pilha (LIFO) de int implementada com lista simplesmente encadeada. */
typedef struct NoPilha {
    int valor;
    struct NoPilha *abaixo;
} NoPilha;

typedef struct {
    NoPilha *topo;
    size_t tam;
} Pilha;

Pilha *pilha_nova(void);
void pilha_liberar(Pilha *p);
bool pilha_empilhar(Pilha *p, int x);
bool pilha_desempilhar(Pilha *p, int *saida);
bool pilha_topo(const Pilha *p, int *saida);
bool pilha_vazia(const Pilha *p);
size_t pilha_tam(const Pilha *p);

#endif
