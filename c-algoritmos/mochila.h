#ifndef MOCHILA_H
#define MOCHILA_H
#include <stddef.h>

/* Mochila 0/1 por programacao dinamica (vetor 1D). Pesos > 0 e valores >= 0.
 * Retorna o valor maximo com capacidade cap; -1 se algum peso for <= 0,
 * cap < 0 ou faltar memoria. Itens mais pesados que cap sao ignorados. */
long mochila(const int *peso, const int *valor, size_t n, int cap);

#endif
