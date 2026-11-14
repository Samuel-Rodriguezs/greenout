#include "bitmap_blocos.h"

#include <stdint.h>
#include <stdlib.h>

struct BitmapBlocos {
    size_t n;
    size_t livres;
    uint8_t *bits;
};

BitmapBlocos *bb_criar(size_t nblocos) {
    if (nblocos == 0) return NULL;
    BitmapBlocos *b = malloc(sizeof *b);
    if (!b) return NULL;
    b->bits = calloc((nblocos + 7) / 8, 1);
    if (!b->bits) {
        free(b);
        return NULL;
    }
    b->n = nblocos;
    b->livres = nblocos;
    return b;
}

void bb_destruir(BitmapBlocos *b) {
    if (!b) return;
    free(b->bits);
    free(b);
}

int bb_ocupado(const BitmapBlocos *b, size_t i) {
    return (b->bits[i / 8] >> (i % 8)) & 1;
}

static void marcar(BitmapBlocos *b, size_t i, int v) {
    if (v) b->bits[i / 8] |= (uint8_t)(1u << (i % 8));
    else b->bits[i / 8] &= (uint8_t)~(1u << (i % 8));
}

long bb_alocar(BitmapBlocos *b) {
    return bb_alocar_contiguo(b, 1);
}

long bb_alocar_contiguo(BitmapBlocos *b, size_t n) {
    if (n == 0 || n > b->livres) return -1;
    size_t corrida = 0;
    for (size_t i = 0; i < b->n; i++) {
        corrida = bb_ocupado(b, i) ? 0 : corrida + 1;
        if (corrida == n) {
            size_t ini = i + 1 - n;
            for (size_t k = ini; k <= i; k++) marcar(b, k, 1);
            b->livres -= n;
            return (long)ini;
        }
    }
    return -1;
}

int bb_liberar(BitmapBlocos *b, size_t ini, size_t n) {
    if (n == 0 || ini >= b->n || n > b->n - ini) return -1;
    for (size_t k = ini; k < ini + n; k++)
        if (!bb_ocupado(b, k)) return -1;
    for (size_t k = ini; k < ini + n; k++) marcar(b, k, 0);
    b->livres += n;
    return 0;
}

size_t bb_livres(const BitmapBlocos *b) { return b->livres; }

size_t bb_maior_extensao(const BitmapBlocos *b) {
    size_t melhor = 0, corrida = 0;
    for (size_t i = 0; i < b->n; i++) {
        corrida = bb_ocupado(b, i) ? 0 : corrida + 1;
        if (corrida > melhor) melhor = corrida;
    }
    return melhor;
}
