#ifndef POOL_H
#define POOL_H
#include <stddef.h>

/* Pool de memoria de blocos de tamanho fixo com free-list intrusiva. */
typedef struct {
    unsigned char *mem;
    size_t tam_bloco, n_blocos;
    void *livre;      /* topo da free-list */
    size_t em_uso;
} Pool;

/* tam_bloco e arredondado para >= sizeof(void*) e multiplo de 16. */
int pool_init(Pool *p, size_t tam_bloco, size_t n_blocos);
/* Retorna um bloco ou NULL se o pool esgotou. */
void *pool_alloc(Pool *p);
/* Devolve um bloco ao pool; retorna -1 se o ponteiro nao pertence ao pool. */
int pool_free(Pool *p, void *ptr);
void pool_destruir(Pool *p);

#endif
