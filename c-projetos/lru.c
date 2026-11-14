#include "lru.h"
#include <stdlib.h>
#include <string.h>

typedef struct No {
    char *chave;
    int valor;
    struct No *prev, *next; /* lista de uso: head = mais recente */
    struct No *hnext;       /* encadeamento do bucket */
} No;

struct Lru {
    size_t cap, n, nb;
    No **b;
    No *head, *tail;
};

static size_t hash(const char *s, size_t nb) {
    size_t h = 5381;
    while (*s) h = h * 33 + (unsigned char)*s++;
    return h % nb;
}

Lru *lru_criar(size_t cap) {
    if (cap == 0) return NULL;
    Lru *c = calloc(1, sizeof *c);
    if (!c) return NULL;
    c->cap = cap;
    c->nb = cap * 2 + 1;
    c->b = calloc(c->nb, sizeof *c->b);
    if (!c->b) { free(c); return NULL; }
    return c;
}

static void lista_remove(Lru *c, No *n) {
    if (n->prev) n->prev->next = n->next; else c->head = n->next;
    if (n->next) n->next->prev = n->prev; else c->tail = n->prev;
}

static void lista_frente(Lru *c, No *n) {
    n->prev = NULL;
    n->next = c->head;
    if (c->head) c->head->prev = n;
    c->head = n;
    if (!c->tail) c->tail = n;
}

static No *busca(const Lru *c, const char *k) {
    for (No *n = c->b[hash(k, c->nb)]; n; n = n->hnext)
        if (!strcmp(n->chave, k)) return n;
    return NULL;
}

static void expulsa(Lru *c, No *n) {
    No **pp = &c->b[hash(n->chave, c->nb)];
    while (*pp != n) pp = &(*pp)->hnext;
    *pp = n->hnext;
    lista_remove(c, n);
    free(n->chave);
    free(n);
    c->n--;
}

void lru_liberar(Lru *c) {
    if (!c) return;
    for (No *n = c->head, *p; n; n = p) {
        p = n->next;
        free(n->chave);
        free(n);
    }
    free(c->b);
    free(c);
}

int lru_put(Lru *c, const char *k, int v) {
    No *n = busca(c, k);
    if (n) {
        n->valor = v;
        lista_remove(c, n);
        lista_frente(c, n);
        return 0;
    }
    if (c->n == c->cap) expulsa(c, c->tail);
    n = malloc(sizeof *n);
    if (!n) return -1;
    n->chave = malloc(strlen(k) + 1);
    if (!n->chave) { free(n); return -1; }
    strcpy(n->chave, k);
    n->valor = v;
    size_t h = hash(k, c->nb);
    n->hnext = c->b[h];
    c->b[h] = n;
    lista_frente(c, n);
    c->n++;
    return 0;
}

int lru_get(Lru *c, const char *k, int *v) {
    No *n = busca(c, k);
    if (!n) return 0;
    lista_remove(c, n);
    lista_frente(c, n);
    *v = n->valor;
    return 1;
}

size_t lru_tamanho(const Lru *c) { return c->n; }
const char *lru_mais_antiga(const Lru *c) { return c->tail ? c->tail->chave : NULL; }
