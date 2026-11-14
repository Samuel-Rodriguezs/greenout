#ifndef LEVENSHTEIN_H
#define LEVENSHTEIN_H
#include <stddef.h>

/* Distancia de edicao (insercao, remocao, substituicao, custo 1 cada)
 * entre duas strings, com DP de duas linhas (memoria O(min(m,n))).
 * Retorna (size_t)-1 se faltar memoria. */
size_t levenshtein(const char *a, const char *b);

#endif
