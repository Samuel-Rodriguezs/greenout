#ifndef BIGNUM_H
#define BIGNUM_H

/* Aritmetica de naturais arbitrariamente grandes em strings decimais.
 * Entradas devem conter so digitos '0'-'9' (nao vazias); zeros a esquerda
 * sao aceitos e removidos no resultado. Todas retornam string alocada
 * (liberar com free) ou NULL se a entrada for invalida / faltar memoria. */
char *big_soma(const char *a, const char *b);
char *big_mul(const char *a, const char *b);
char *big_fatorial(unsigned n);

#endif
