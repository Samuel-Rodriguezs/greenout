#ifndef PILHA_H
#define PILHA_H

#include <stdbool.h>
#include <stddef.h>

#define PILHA_CAPACIDADE 8

/* Pilha de inteiros com capacidade fixa, armazenada em array. */
typedef struct {
    int dados[PILHA_CAPACIDADE];
    size_t topo; /* quantidade de elementos */
} Pilha;

void pilha_init(Pilha *p);
bool pilha_vazia(const Pilha *p);
bool pilha_cheia(const Pilha *p);
size_t pilha_tamanho(const Pilha *p);

/* Empilha; devolve false se estiver cheia. */
bool pilha_push(Pilha *p, int valor);

/* Desempilha em *valor; devolve false se estiver vazia. */
bool pilha_pop(Pilha *p, int *valor);

/* Le o topo em *valor sem remover; devolve false se estiver vazia. */
bool pilha_topo(const Pilha *p, int *valor);

#endif
