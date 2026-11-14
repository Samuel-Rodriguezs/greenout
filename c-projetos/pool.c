#include "pool.h"
#include <stdlib.h>

int pool_init(Pool *p, size_t tam_bloco, size_t n_blocos) {
    if (n_blocos == 0) return -1;
    if (tam_bloco < sizeof(void *)) tam_bloco = sizeof(void *);
    tam_bloco = (tam_bloco + 15) & ~(size_t)15;
    if (tam_bloco > (size_t)-1 / n_blocos) return -1;
    /* aligned_alloc exige tamanho multiplo do alinhamento: ok (multiplo de 16). */
    p->mem = aligned_alloc(16, tam_bloco * n_blocos);
    if (!p->mem) return -1;
    p->tam_bloco = tam_bloco;
    p->n_blocos = n_blocos;
    p->em_uso = 0;
    /* Encadeia todos os blocos na free-list. */
    p->livre = NULL;
    for (size_t i = n_blocos; i-- > 0;) {
        void **b = (void **)(p->mem + i * tam_bloco);
        *b = p->livre;
        p->livre = b;
    }
    return 0;
}

void *pool_alloc(Pool *p) {
    void **b = p->livre;
    if (!b) return NULL;
    p->livre = *b;
    p->em_uso++;
    return b;
}

int pool_free(Pool *p, void *ptr) {
    unsigned char *c = ptr;
    if (!ptr || c < p->mem || c >= p->mem + p->tam_bloco * p->n_blocos ||
        (size_t)(c - p->mem) % p->tam_bloco != 0)
        return -1;
    void **b = ptr;
    *b = p->livre;
    p->livre = b;
    p->em_uso--;
    return 0;
}

void pool_destruir(Pool *p) {
    free(p->mem);
    p->mem = NULL;
    p->livre = NULL;
    p->em_uso = 0;
}
