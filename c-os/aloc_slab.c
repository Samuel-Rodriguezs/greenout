#include "aloc_slab.h"

#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef struct Slab {
    unsigned char *mem;  /* objs_por_slab * tam_obj bytes */
    size_t *pilha_livres; /* indices livres (pilha) */
    unsigned char *usado; /* detecta duplo free */
    size_t n_livres;
    struct Slab *prox;
} Slab;

struct SlabCache {
    size_t tam_obj;
    size_t por_slab;
    Slab *slabs;
    size_t num_slabs;
    size_t em_uso;
};

static Slab *slab_novo(const SlabCache *c) {
    Slab *s = malloc(sizeof *s);
    if (!s) return NULL;
    s->mem = malloc(c->tam_obj * c->por_slab);
    s->pilha_livres = malloc(c->por_slab * sizeof(size_t));
    s->usado = calloc(c->por_slab, 1);
    if (!s->mem || !s->pilha_livres || !s->usado) {
        free(s->mem);
        free(s->pilha_livres);
        free(s->usado);
        free(s);
        return NULL;
    }
    /* topo da pilha = indice 0, entao os objetos saem em ordem crescente */
    for (size_t i = 0; i < c->por_slab; i++) s->pilha_livres[i] = c->por_slab - 1 - i;
    s->n_livres = c->por_slab;
    s->prox = NULL;
    return s;
}

static void slab_free(Slab *s) {
    free(s->mem);
    free(s->pilha_livres);
    free(s->usado);
    free(s);
}

SlabCache *slab_criar(size_t tam_obj, size_t objs_por_slab) {
    if (tam_obj == 0 || objs_por_slab == 0) return NULL;
    SlabCache *c = calloc(1, sizeof *c);
    if (!c) return NULL;
    c->tam_obj = tam_obj;
    c->por_slab = objs_por_slab;
    return c;
}

void slab_destruir(SlabCache *c) {
    if (!c) return;
    Slab *s = c->slabs;
    while (s) {
        Slab *p = s->prox;
        slab_free(s);
        s = p;
    }
    free(c);
}

void *slab_alocar(SlabCache *c) {
    Slab *s = c->slabs;
    while (s && s->n_livres == 0) s = s->prox; /* primeiro slab com vaga */
    if (!s) {
        s = slab_novo(c);
        if (!s) return NULL;
        s->prox = c->slabs;
        c->slabs = s;
        c->num_slabs++;
    }
    size_t i = s->pilha_livres[--s->n_livres];
    s->usado[i] = 1;
    c->em_uso++;
    void *p = s->mem + i * c->tam_obj;
    memset(p, 0, c->tam_obj);
    return p;
}

int slab_liberar(SlabCache *c, void *obj) {
    if (!c || !obj) return -1;
    uintptr_t addr = (uintptr_t)obj;
    for (Slab *s = c->slabs; s; s = s->prox) {
        uintptr_t ini = (uintptr_t)s->mem;
        if (addr < ini || addr >= ini + c->tam_obj * c->por_slab) continue;
        if ((addr - ini) % c->tam_obj) return -1;
        size_t i = (addr - ini) / c->tam_obj;
        if (!s->usado[i]) return -1;
        s->usado[i] = 0;
        s->pilha_livres[s->n_livres++] = i;
        c->em_uso--;
        return 0;
    }
    return -1;
}

size_t slab_recolher(SlabCache *c) {
    size_t n = 0;
    Slab **pp = &c->slabs;
    while (*pp) {
        Slab *s = *pp;
        if (s->n_livres == c->por_slab) {
            *pp = s->prox;
            slab_free(s);
            c->num_slabs--;
            n++;
        } else {
            pp = &s->prox;
        }
    }
    return n;
}

size_t slab_num_slabs(const SlabCache *c) { return c->num_slabs; }
size_t slab_em_uso(const SlabCache *c) { return c->em_uso; }
