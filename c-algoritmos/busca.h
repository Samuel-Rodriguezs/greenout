#ifndef BUSCA_H
#define BUSCA_H
#include <stddef.h>

/* Ambas exigem a[0..n) ordenado crescente. Retornam o indice de uma
 * ocorrencia de chave, ou -1 se nao existir. */
long busca_binaria(const int *a, size_t n, int chave);
long busca_interpolacao(const int *a, size_t n, int chave);

/* Primeiro indice cujo valor >= chave (n se nenhum): limite inferior. */
size_t busca_limite_inferior(const int *a, size_t n, int chave);

#endif
