#ifndef BITMAP_BLOCOS_H
#define BITMAP_BLOCOS_H

#include <stddef.h>

/* Bitmap de blocos livres (como o de um sistema de arquivos):
 * bit 0 = livre, bit 1 = ocupado. */

typedef struct BitmapBlocos BitmapBlocos;

BitmapBlocos *bb_criar(size_t nblocos);
void bb_destruir(BitmapBlocos *b);

/* Aloca o primeiro bloco livre; retorna o indice ou -1. */
long bb_alocar(BitmapBlocos *b);
/* Aloca `n` blocos contiguos (primeira sequencia que couber); retorna o
 * indice inicial ou -1. */
long bb_alocar_contiguo(BitmapBlocos *b, size_t n);
/* Libera `n` blocos a partir de `ini`; -1 se fora dos limites ou se algum
 * bloco ja estava livre (nada e alterado nesse caso). */
int bb_liberar(BitmapBlocos *b, size_t ini, size_t n);

int bb_ocupado(const BitmapBlocos *b, size_t i);
size_t bb_livres(const BitmapBlocos *b);
/* Maior sequencia contigua de blocos livres. */
size_t bb_maior_extensao(const BitmapBlocos *b);

#endif
