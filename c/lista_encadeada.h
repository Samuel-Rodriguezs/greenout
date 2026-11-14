#ifndef LISTA_ENCADEADA_H
#define LISTA_ENCADEADA_H

#include <stdbool.h>
#include <stddef.h>

typedef struct No {
    int valor;
    struct No *prox;
} No;

/* Insere no inicio; devolve a nova cabeca (a lista original, inalterada,
 * se malloc falhar). */
No *lista_inserir_inicio(No *lista, int valor);

/* Insere no fim; devolve a cabeca (inalterada, ou o novo no se vazia). */
No *lista_inserir_fim(No *lista, int valor);

/* Remove a primeira ocorrencia de valor; *removido indica se achou.
 * Devolve a nova cabeca. */
No *lista_remover(No *lista, int valor, bool *removido);

bool lista_contem(const No *lista, int valor);
size_t lista_tamanho(const No *lista);

/* Inverte a lista in-place e devolve a nova cabeca. */
No *lista_inverter(No *lista);

/* Libera todos os nos. */
void lista_liberar(No *lista);

#endif
