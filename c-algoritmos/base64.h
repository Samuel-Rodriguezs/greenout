#ifndef BASE64_H
#define BASE64_H
#include <stddef.h>
#include <stdint.h>

/* Base64 padrao (RFC 4648, alfabeto A-Za-z0-9+/ com padding '=').
 * Codifica n bytes; retorna string terminada em NUL (free) ou NULL. */
char *base64_codificar(const uint8_t *dados, size_t n);

/* Decodifica string estrita (tamanho multiplo de 4, padding so no fim).
 * Grava o tamanho em *saida_n. Retorna buffer (free) ou NULL se invalida
 * ou sem memoria. Resultado vazio retorna buffer nao-NULL com *saida_n = 0. */
uint8_t *base64_decodificar(const char *texto, size_t *saida_n);

#endif
