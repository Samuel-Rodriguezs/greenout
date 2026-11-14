#ifndef LISTA_DUPLA_H
#define LISTA_DUPLA_H
#include <stdbool.h>
#include <stddef.h>

/* Lista duplamente encadeada de int, com ponteiros para cabeca e cauda. */
typedef struct No {
    int valor;
    struct No *ant;
    struct No *prox;
} No;

typedef struct {
    No *cabeca;
    No *cauda;
    size_t tam;
} Lista;

Lista *lista_nova(void);
void lista_liberar(Lista *l);
size_t lista_tam(const Lista *l);
bool lista_push_frente(Lista *l, int x);
bool lista_push_tras(Lista *l, int x);
bool lista_pop_frente(Lista *l, int *saida);
bool lista_pop_tras(Lista *l, int *saida);
bool lista_obter(const Lista *l, size_t i, int *saida);
bool lista_inserir(Lista *l, size_t i, int x);       /* i <= tam */
bool lista_remover_valor(Lista *l, int x);           /* primeira ocorrencia */
void lista_inverter(Lista *l);

#endif
