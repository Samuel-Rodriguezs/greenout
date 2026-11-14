#ifndef QUICKSORT_H
#define QUICKSORT_H
#include <stddef.h>

/* Ordena a[0..n) em ordem crescente (mediana de tres + insercao em
 * particoes pequenas; recursa so no lado menor, pilha O(log n)). */
void quicksort(int *a, size_t n);

#endif
