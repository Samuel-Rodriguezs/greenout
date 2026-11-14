#ifndef COUNTINGSORT_H
#define COUNTINGSORT_H
#include <stddef.h>

/* Counting sort para inteiros (aceita negativos). Retorna 0 em sucesso;
 * -1 se faltar memoria ou se a faixa (max-min+1) passar de 50 milhoes. */
int countingsort(int *a, size_t n);

#endif
