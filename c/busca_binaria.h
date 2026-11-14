#ifndef BUSCA_BINARIA_H
#define BUSCA_BINARIA_H

#include <stddef.h>

/* Busca `alvo` em vetor ordenado de forma crescente. Devolve o indice ou -1. */
long busca_binaria(const int *v, size_t n, int alvo);

#endif
