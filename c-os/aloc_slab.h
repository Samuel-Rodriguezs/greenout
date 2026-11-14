#ifndef ALOC_SLAB_H
#define ALOC_SLAB_H

#include <stddef.h>

/* Alocador slab simulado: um cache de objetos de tamanho fixo. Cada slab
 * guarda `objs_por_slab` objetos e uma lista de objetos livres; o cache
 * prefere slabs parciais e so cria um slab novo quando todos estao cheios. */

typedef struct SlabCache SlabCache;

SlabCache *slab_criar(size_t tam_obj, size_t objs_por_slab);
void slab_destruir(SlabCache *c);

/* Retorna um objeto zerado ou NULL. */
void *slab_alocar(SlabCache *c);
/* 0 = ok; -1 = ponteiro que nao pertence ao cache, desalinhado ou ja livre. */
int slab_liberar(SlabCache *c, void *obj);
/* Devolve ao sistema os slabs totalmente vazios; retorna quantos. */
size_t slab_recolher(SlabCache *c);

size_t slab_num_slabs(const SlabCache *c);
size_t slab_em_uso(const SlabCache *c);

#endif
