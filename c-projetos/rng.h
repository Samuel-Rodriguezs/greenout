#ifndef RNG_H
#define RNG_H
#include <stdint.h>

/* Geradores pseudoaleatorios deterministicos a partir de uma semente. */
typedef struct { uint64_t s; } Xorshift;                 /* xorshift64* */
typedef struct { uint64_t estado, inc; } Pcg32;          /* PCG-XSH-RR */

void xs_seed(Xorshift *r, uint64_t seed);
uint64_t xs_next(Xorshift *r);

void pcg_seed(Pcg32 *r, uint64_t seed, uint64_t seq);
uint32_t pcg_next(Pcg32 *r);

/* Double uniforme em [0, 1). */
double pcg_double(Pcg32 *r);
/* Inteiro uniforme em [0, limite) sem vies (limite > 0). */
uint32_t pcg_limitado(Pcg32 *r, uint32_t limite);

/* Testes estatisticos simples sobre n amostras de pcg_limitado(r, k):
 * qui-quadrado dos k baldes (k-1 graus de liberdade). */
double rng_qui_quadrado(Pcg32 *r, uint32_t k, uint32_t n);
/* Media de n amostras de pcg_double (esperado ~0.5). */
double rng_media(Pcg32 *r, uint32_t n);

#endif
