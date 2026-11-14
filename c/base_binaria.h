#ifndef BASE_BINARIA_H
#define BASE_BINARIA_H

#include <stddef.h>

/* Converte n (>= 0) de base 10 para binario em `saida` (string terminada em
 * '\0'). Devolve 0 em sucesso ou -1 se o buffer (tamanho `cap`, incluindo o
 * '\0') for pequeno demais. */
int decimal_para_binario(unsigned long n, char *saida, size_t cap);

#endif
