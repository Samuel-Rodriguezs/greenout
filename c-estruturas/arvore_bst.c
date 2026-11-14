#include "arvore_bst.h"
#include <stdlib.h>

Bst *bst_nova(void) {
    Bst *b = malloc(sizeof *b);
    if (!b) return NULL;
    b->raiz = NULL;
    b->tam = 0;
    return b;
}

static void liberar_no(NoBst *n) {
    if (!n) return;
    liberar_no(n->esq);
    liberar_no(n->dir);
    free(n);
}

void bst_liberar(Bst *b) {
    if (!b) return;
    liberar_no(b->raiz);
    free(b);
}

size_t bst_tam(const Bst *b) { return b->tam; }

bool bst_inserir(Bst *b, int chave) {
    NoBst **pp = &b->raiz;
    while (*pp) {
        if (chave == (*pp)->chave) return false;
        pp = chave < (*pp)->chave ? &(*pp)->esq : &(*pp)->dir;
    }
    NoBst *n = malloc(sizeof *n);
    if (!n) return false;
    n->chave = chave;
    n->esq = n->dir = NULL;
    *pp = n;
    b->tam++;
    return true;
}

bool bst_buscar(const Bst *b, int chave) {
    const NoBst *n = b->raiz;
    while (n) {
        if (chave == n->chave) return true;
        n = chave < n->chave ? n->esq : n->dir;
    }
    return false;
}

bool bst_remover(Bst *b, int chave) {
    NoBst **pp = &b->raiz;
    while (*pp && (*pp)->chave != chave)
        pp = chave < (*pp)->chave ? &(*pp)->esq : &(*pp)->dir;
    NoBst *n = *pp;
    if (!n) return false;
    if (!n->esq) {
        *pp = n->dir;
    } else if (!n->dir) {
        *pp = n->esq;
    } else {
        /* Dois filhos: substitui pelo sucessor (menor da subarvore direita). */
        NoBst **ps = &n->dir;
        while ((*ps)->esq) ps = &(*ps)->esq;
        NoBst *suc = *ps;
        *ps = suc->dir;
        suc->esq = n->esq;
        suc->dir = n->dir;
        *pp = suc;
    }
    free(n);
    b->tam--;
    return true;
}

bool bst_minimo(const Bst *b, int *saida) {
    const NoBst *n = b->raiz;
    if (!n) return false;
    while (n->esq) n = n->esq;
    *saida = n->chave;
    return true;
}

bool bst_maximo(const Bst *b, int *saida) {
    const NoBst *n = b->raiz;
    if (!n) return false;
    while (n->dir) n = n->dir;
    *saida = n->chave;
    return true;
}

static int altura_no(const NoBst *n) {
    if (!n) return 0;
    int e = altura_no(n->esq), d = altura_no(n->dir);
    return 1 + (e > d ? e : d);
}

int bst_altura(const Bst *b) { return altura_no(b->raiz); }

static void em_ordem_no(const NoBst *n, int *saida, size_t cap, size_t *k) {
    if (!n) return;
    em_ordem_no(n->esq, saida, cap, k);
    if (*k < cap) saida[*k] = n->chave;
    (*k)++;
    em_ordem_no(n->dir, saida, cap, k);
}

size_t bst_em_ordem(const Bst *b, int *saida, size_t cap) {
    size_t k = 0;
    em_ordem_no(b->raiz, saida, cap, &k);
    return k < cap ? k : cap;
}
