#ifndef KMP_H
#define KMP_H
#include <stddef.h>

/* Primeiro indice de padrao em texto (Knuth-Morris-Pratt), -1 se ausente.
 * Padrao vazio casa em 0. Retorna -2 se faltar memoria. */
long kmp_buscar(const char *texto, const char *padrao);

/* Numero de ocorrencias (inclui sobrepostas). Padrao vazio -> 0.
 * Retorna -1 se faltar memoria. */
long kmp_contar(const char *texto, const char *padrao);

#endif
