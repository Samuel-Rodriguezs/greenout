#ifndef FILA_PRIORIDADE_H
#define FILA_PRIORIDADE_H
#include <stdbool.h>
#include <stddef.h>

/* Fila de prioridade (maior prioridade sai primeiro). Empates sao resolvidos
 * por ordem de chegada (estavel), usando um numero de sequencia crescente. */
typedef struct {
    int valor;
    int prioridade;
    unsigned long seq;
} ItemPq;

typedef struct {
    ItemPq *itens;
    size_t tam;
    size_t cap;
    unsigned long prox_seq;
} Pq;

Pq *pq_nova(void);
void pq_liberar(Pq *q);
size_t pq_tam(const Pq *q);
bool pq_inserir(Pq *q, int valor, int prioridade);
bool pq_espiar(const Pq *q, int *valor, int *prioridade);
bool pq_remover(Pq *q, int *valor, int *prioridade);

#endif
