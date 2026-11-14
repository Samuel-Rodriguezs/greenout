#ifndef CRIVO_H
#define CRIVO_H

#include <stddef.h>

/* Crivo de Eratostenes: grava em `saida` (capacidade `cap`) os primos <= limite
 * em ordem crescente e devolve quantos primos existem ate `limite`
 * (mesmo que `cap` seja menor e nem todos tenham sido gravados).
 * Devolve 0 em caso de limite < 2 ou falha de alocacao. */
size_t crivo_primos(unsigned limite, unsigned *saida, size_t cap);

#endif
