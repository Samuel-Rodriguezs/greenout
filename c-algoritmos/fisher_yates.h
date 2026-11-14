#ifndef FISHER_YATES_H
#define FISHER_YATES_H
#include <stddef.h>
#include <stdint.h>

/* PRNG xorshift32 (Marsaglia: 13, 17, 5). Deterministico a partir da seed. */
typedef struct { uint32_t estado; } Xorshift;

/* Seed 0 e substituida por uma constante (xorshift nao aceita estado 0). */
void xorshift_iniciar(Xorshift *g, uint32_t seed);
uint32_t xorshift_proximo(Xorshift *g);

/* Inteiro uniforme em [0, limite) por rejeicao (sem vies de modulo).
 * limite == 0 retorna 0. */
uint32_t xorshift_ate(Xorshift *g, uint32_t limite);

/* Embaralhamento de Fisher-Yates in-place; mesma seed => mesma permutacao. */
void embaralhar(int *a, size_t n, Xorshift *g);

#endif
