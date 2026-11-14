#ifndef MERGESORT_H
#define MERGESORT_H
#include <stddef.h>

/* Ordena a[0..n) de forma estavel e crescente. Retorna 0 em sucesso,
 * -1 se faltar memoria para o buffer auxiliar (a fica intacto). */
int mergesort_int(int *a, size_t n);

#endif
