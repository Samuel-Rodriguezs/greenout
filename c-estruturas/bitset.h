#ifndef BITSET_H
#define BITSET_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Conjunto de bits de tamanho fixo (indices 0..n-1), em palavras de 64 bits. */
typedef struct {
    uint64_t *palavras;
    size_t n;          /* numero de bits */
} Bitset;

Bitset *bitset_novo(size_t n);
void bitset_liberar(Bitset *b);
size_t bitset_tamanho(const Bitset *b);
bool bitset_definir(Bitset *b, size_t i);     /* false se i fora do intervalo */
bool bitset_limpar(Bitset *b, size_t i);
bool bitset_alternar(Bitset *b, size_t i);
bool bitset_testar(const Bitset *b, size_t i);   /* false se fora do intervalo */
size_t bitset_contar(const Bitset *b);        /* quantos bits ligados */
/* Primeiro bit ligado a partir de 'de'; devolve n se nao houver. */
size_t bitset_proximo(const Bitset *b, size_t de);
/* Operacoes em lote; exigem o mesmo tamanho (false caso contrario). Alteram a. */
bool bitset_e(Bitset *a, const Bitset *b);
bool bitset_ou(Bitset *a, const Bitset *b);
bool bitset_xor(Bitset *a, const Bitset *b);
void bitset_inverter(Bitset *b);              /* complemento dentro de 0..n-1 */

#endif
