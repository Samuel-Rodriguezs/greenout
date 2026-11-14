#ifndef RLE_H
#define RLE_H
#include <stddef.h>
#include <stdint.h>

/* Run-length encoding binario: saida e uma sequencia de pares
 * (contagem 1..255, byte). Funciona com qualquer byte, inclusive 0 e digitos.
 * Retorna buffer alocado (free) e grava o tamanho em *saida_n; NULL se
 * faltar memoria. Entrada vazia gera buffer vazio (nao NULL). */
uint8_t *rle_codificar(const uint8_t *entrada, size_t n, size_t *saida_n);

/* Inverso. NULL se a entrada for malformada (tamanho impar ou contagem 0)
 * ou faltar memoria. */
uint8_t *rle_decodificar(const uint8_t *entrada, size_t n, size_t *saida_n);

#endif
