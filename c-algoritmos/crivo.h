#ifndef CRIVO_H
#define CRIVO_H
#include <stddef.h>

/* Crivo de Eratostenes com bitset (1 bit por numero impar nao-composto).
 * Crivo e opaco; crie com crivo_criar e libere com crivo_liberar. */
typedef struct Crivo Crivo;

/* Marca primos em [0, limite]. NULL se faltar memoria. */
Crivo *crivo_criar(size_t limite);
void crivo_liberar(Crivo *c);

/* 1 se n for primo, 0 caso contrario (inclusive n > limite). */
int crivo_eh_primo(const Crivo *c, size_t n);

/* Quantidade de primos em [0, limite]. */
size_t crivo_contar(const Crivo *c);

#endif
