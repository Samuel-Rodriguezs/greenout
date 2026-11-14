#ifndef MDC_MODULAR_H
#define MDC_MODULAR_H
#include <stdint.h>

/* MDC (Euclides) e MMC. mmc(0, x) = 0. Sem overflow garantido so se o
 * resultado couber em uint64_t. */
uint64_t mdc(uint64_t a, uint64_t b);
uint64_t mmc(uint64_t a, uint64_t b);

/* (base ^ exp) mod m por exponenciacao rapida; usa 128 bits no produto,
 * entao vale para qualquer m < 2^64. m == 0 retorna 0 (invalido). */
uint64_t exp_mod(uint64_t base, uint64_t exp, uint64_t m);

/* Inverso modular de a mod m (Euclides estendido). Retorna 0 se nao
 * existir (mdc(a, m) != 1) ou m < 2; caso contrario valor em [1, m-1]. */
uint64_t inverso_mod(uint64_t a, uint64_t m);

#endif
