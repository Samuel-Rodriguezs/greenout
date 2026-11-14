#include "bitset.h"
#include <stdlib.h>

#define BITS 64

static size_t num_palavras(size_t n) { return (n + BITS - 1) / BITS; }

Bitset *bitset_novo(size_t n) {
    Bitset *b = malloc(sizeof *b);
    if (!b) return NULL;
    size_t np = num_palavras(n);
    b->palavras = calloc(np ? np : 1, sizeof(uint64_t));
    if (!b->palavras) {
        free(b);
        return NULL;
    }
    b->n = n;
    return b;
}

void bitset_liberar(Bitset *b) {
    if (!b) return;
    free(b->palavras);
    free(b);
}

size_t bitset_tamanho(const Bitset *b) { return b->n; }

bool bitset_definir(Bitset *b, size_t i) {
    if (i >= b->n) return false;
    b->palavras[i / BITS] |= (uint64_t)1 << (i % BITS);
    return true;
}

bool bitset_limpar(Bitset *b, size_t i) {
    if (i >= b->n) return false;
    b->palavras[i / BITS] &= ~((uint64_t)1 << (i % BITS));
    return true;
}

bool bitset_alternar(Bitset *b, size_t i) {
    if (i >= b->n) return false;
    b->palavras[i / BITS] ^= (uint64_t)1 << (i % BITS);
    return true;
}

bool bitset_testar(const Bitset *b, size_t i) {
    if (i >= b->n) return false;
    return (b->palavras[i / BITS] >> (i % BITS)) & 1;
}

size_t bitset_contar(const Bitset *b) {
    size_t total = 0;
    for (size_t i = 0; i < num_palavras(b->n); i++) {
        uint64_t w = b->palavras[i];
        while (w) {            /* algoritmo de Kernighan */
            w &= w - 1;
            total++;
        }
    }
    return total;
}

size_t bitset_proximo(const Bitset *b, size_t de) {
    for (size_t i = de; i < b->n; i++) {
        if (i % BITS == 0 && b->palavras[i / BITS] == 0) {
            i += BITS - 1;    /* pula palavra inteira vazia */
            continue;
        }
        if (bitset_testar(b, i)) return i;
    }
    return b->n;
}

/* Zera os bits sobrando na ultima palavra (mantem a invariante para contar). */
static void mascarar(Bitset *b) {
    size_t resto = b->n % BITS;
    if (resto) b->palavras[num_palavras(b->n) - 1] &= ((uint64_t)1 << resto) - 1;
}

bool bitset_e(Bitset *a, const Bitset *b) {
    if (a->n != b->n) return false;
    for (size_t i = 0; i < num_palavras(a->n); i++) a->palavras[i] &= b->palavras[i];
    return true;
}

bool bitset_ou(Bitset *a, const Bitset *b) {
    if (a->n != b->n) return false;
    for (size_t i = 0; i < num_palavras(a->n); i++) a->palavras[i] |= b->palavras[i];
    return true;
}

bool bitset_xor(Bitset *a, const Bitset *b) {
    if (a->n != b->n) return false;
    for (size_t i = 0; i < num_palavras(a->n); i++) a->palavras[i] ^= b->palavras[i];
    return true;
}

void bitset_inverter(Bitset *b) {
    for (size_t i = 0; i < num_palavras(b->n); i++) b->palavras[i] = ~b->palavras[i];
    mascarar(b);
}
