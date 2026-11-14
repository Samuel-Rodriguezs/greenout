#ifndef RADIXSORT_H
#define RADIXSORT_H
#include <stddef.h>
#include <stdint.h>

/* Radix sort LSD (base 256, 4 passadas) para uint32_t. Estavel.
 * Retorna 0 em sucesso, -1 se faltar memoria. */
int radixsort_u32(uint32_t *a, size_t n);

#endif
