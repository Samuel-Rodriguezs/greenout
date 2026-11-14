#include "avl.h"
#include <limits.h>
#include <stdlib.h>

Avl *avl_nova(void) {
    Avl *a = malloc(sizeof *a);
    if (!a) return NULL;
    a->raiz = NULL;
    a->tam = 0;
    return a;
}

static void liberar_no(NoAvl *n) {
    if (!n) return;
    liberar_no(n->esq);
    liberar_no(n->dir);
    free(n);
}

void avl_liberar(Avl *a) {
    if (!a) return;
    liberar_no(a->raiz);
    free(a);
}

size_t avl_tam(const Avl *a) { return a->tam; }

static int alt(const NoAvl *n) { return n ? n->altura : 0; }
static int max2(int a, int b) { return a > b ? a : b; }
static void atualizar(NoAvl *n) { n->altura = 1 + max2(alt(n->esq), alt(n->dir)); }
static int balanco(const NoAvl *n) { return alt(n->esq) - alt(n->dir); }

static NoAvl *rot_dir(NoAvl *y) {
    NoAvl *x = y->esq;
    y->esq = x->dir;
    x->dir = y;
    atualizar(y);
    atualizar(x);
    return x;
}

static NoAvl *rot_esq(NoAvl *x) {
    NoAvl *y = x->dir;
    x->dir = y->esq;
    y->esq = x;
    atualizar(x);
    atualizar(y);
    return y;
}

/* Reequilibra o no (casos LL, LR, RR, RL) e devolve a nova raiz da subarvore. */
static NoAvl *rebalancear(NoAvl *n) {
    atualizar(n);
    int b = balanco(n);
    if (b > 1) {
        if (balanco(n->esq) < 0) n->esq = rot_esq(n->esq);
        return rot_dir(n);
    }
    if (b < -1) {
        if (balanco(n->dir) > 0) n->dir = rot_dir(n->dir);
        return rot_esq(n);
    }
    return n;
}

/* Retorna a nova raiz; *ok indica se inseriu; *erro indica falta de memoria. */
static NoAvl *inserir_no(NoAvl *n, int chave, bool *ok) {
    if (!n) {
        NoAvl *novo = malloc(sizeof *novo);
        if (!novo) return NULL;
        novo->chave = chave;
        novo->altura = 1;
        novo->esq = novo->dir = NULL;
        *ok = true;
        return novo;
    }
    if (chave < n->chave) n->esq = inserir_no(n->esq, chave, ok);
    else if (chave > n->chave) n->dir = inserir_no(n->dir, chave, ok);
    else return n;
    return rebalancear(n);
}

bool avl_inserir(Avl *a, int chave) {
    bool ok = false;
    a->raiz = inserir_no(a->raiz, chave, &ok);
    if (ok) a->tam++;
    return ok;
}

bool avl_buscar(const Avl *a, int chave) {
    const NoAvl *n = a->raiz;
    while (n) {
        if (chave == n->chave) return true;
        n = chave < n->chave ? n->esq : n->dir;
    }
    return false;
}

/* Remove e devolve o menor no da subarvore em *min (sem liberar). */
static NoAvl *extrair_min(NoAvl *n, NoAvl **min) {
    if (!n->esq) {
        *min = n;
        return n->dir;
    }
    n->esq = extrair_min(n->esq, min);
    return rebalancear(n);
}

static NoAvl *remover_no(NoAvl *n, int chave, bool *ok) {
    if (!n) return NULL;
    if (chave < n->chave) {
        n->esq = remover_no(n->esq, chave, ok);
    } else if (chave > n->chave) {
        n->dir = remover_no(n->dir, chave, ok);
    } else {
        *ok = true;
        NoAvl *esq = n->esq, *dir = n->dir;
        free(n);
        if (!esq) return dir;
        if (!dir) return esq;
        NoAvl *suc;
        dir = extrair_min(dir, &suc);
        suc->esq = esq;
        suc->dir = dir;
        return rebalancear(suc);
    }
    return rebalancear(n);
}

bool avl_remover(Avl *a, int chave) {
    bool ok = false;
    a->raiz = remover_no(a->raiz, chave, &ok);
    if (ok) a->tam--;
    return ok;
}

int avl_altura(const Avl *a) { return alt(a->raiz); }

static bool valida_no(const NoAvl *n, long lo, long hi, int *altura) {
    if (!n) {
        *altura = 0;
        return true;
    }
    if (n->chave <= lo || n->chave >= hi) return false;
    int he, hd;
    if (!valida_no(n->esq, lo, n->chave, &he)) return false;
    if (!valida_no(n->dir, n->chave, hi, &hd)) return false;
    if (he - hd > 1 || hd - he > 1) return false;
    *altura = 1 + max2(he, hd);
    return n->altura == *altura;
}

bool avl_valida(const Avl *a) {
    int h;
    return valida_no(a->raiz, (long)INT_MIN - 1, (long)INT_MAX + 1, &h);
}

static void em_ordem_no(const NoAvl *n, int *saida, size_t cap, size_t *k) {
    if (!n) return;
    em_ordem_no(n->esq, saida, cap, k);
    if (*k < cap) saida[*k] = n->chave;
    (*k)++;
    em_ordem_no(n->dir, saida, cap, k);
}

size_t avl_em_ordem(const Avl *a, int *saida, size_t cap) {
    size_t k = 0;
    em_ordem_no(a->raiz, saida, cap, &k);
    return k < cap ? k : cap;
}
