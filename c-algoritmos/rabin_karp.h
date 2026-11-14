#ifndef RABIN_KARP_H
#define RABIN_KARP_H
#include <stddef.h>

/* Primeiro indice de padrao em texto via hash rolante (Rabin-Karp), -1 se
 * ausente. Padrao vazio casa em 0. Colisoes sao verificadas com memcmp. */
long rabin_karp_buscar(const char *texto, const char *padrao);

/* Numero de ocorrencias (inclui sobrepostas). Padrao vazio -> 0. */
long rabin_karp_contar(const char *texto, const char *padrao);

#endif
