#include "arena.h"
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

#define ALINH 16

struct Bloco {
    Bloco *prev;
    size_t cap, usado;
    _Alignas(ALINH) unsigned char dados[];
};

void arena_init(Arena *a, size_t tam_bloco) {
    a->atual = NULL;
    a->tam_bloco = tam_bloco ? tam_bloco : 4096;
}

void *arena_alloc(Arena *a, size_t n) {
    size_t r = (n + ALINH - 1) & ~(size_t)(ALINH - 1);
    if (r < n) return NULL; /* overflow */
    if (!a->atual || a->atual->cap - a->atual->usado < r) {
        size_t cap = r > a->tam_bloco ? r : a->tam_bloco;
        Bloco *b = malloc(sizeof *b + cap);
        if (!b) return NULL;
        b->prev = a->atual;
        b->cap = cap;
        b->usado = 0;
        a->atual = b;
    }
    void *p = a->atual->dados + a->atual->usado;
    a->atual->usado += r;
    return p;
}

char *arena_strdup(Arena *a, const char *s) {
    size_t l = strlen(s) + 1;
    char *p = arena_alloc(a, l);
    if (p) memcpy(p, s, l);
    return p;
}

void arena_destruir(Arena *a) {
    for (Bloco *b = a->atual, *p; b; b = p) {
        p = b->prev;
        free(b);
    }
    a->atual = NULL;
}

size_t arena_usado(const Arena *a) {
    size_t t = 0;
    for (Bloco *b = a->atual; b; b = b->prev) t += b->usado;
    return t;
}
