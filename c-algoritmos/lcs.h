#ifndef LCS_H
#define LCS_H
#include <stddef.h>

/* Tamanho da maior subsequencia comum (DP). (size_t)-1 se faltar memoria. */
size_t lcs_tamanho(const char *a, const char *b);

/* A propria subsequencia, em string alocada (liberar com free).
 * NULL se faltar memoria. */
char *lcs_string(const char *a, const char *b);

#endif
