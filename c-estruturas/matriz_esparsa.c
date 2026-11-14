#include "matriz_esparsa.h"
#include <stdlib.h>

Matriz *matriz_nova(size_t linhas, size_t colunas) {
    Matriz *m = malloc(sizeof *m);
    if (!m) return NULL;
    m->linha = calloc(linhas ? linhas : 1, sizeof *m->linha);
    if (!m->linha) {
        free(m);
        return NULL;
    }
    m->linhas = linhas;
    m->colunas = colunas;
    m->nnz = 0;
    return m;
}

void matriz_liberar(Matriz *m) {
    if (!m) return;
    for (size_t i = 0; i < m->linhas; i++) {
        Celula *c = m->linha[i];
        while (c) {
            Celula *p = c->prox;
            free(c);
            c = p;
        }
    }
    free(m->linha);
    free(m);
}

size_t matriz_nnz(const Matriz *m) { return m->nnz; }

bool matriz_definir(Matriz *m, size_t i, size_t j, double valor) {
    if (i >= m->linhas || j >= m->colunas) return false;
    Celula **pp = &m->linha[i];
    while (*pp && (*pp)->col < j) pp = &(*pp)->prox;
    Celula *c = *pp;
    if (c && c->col == j) {
        if (valor == 0.0) {         /* remove */
            *pp = c->prox;
            free(c);
            m->nnz--;
        } else {
            c->valor = valor;
        }
        return true;
    }
    if (valor == 0.0) return true;  /* ja era zero */
    Celula *n = malloc(sizeof *n);
    if (!n) return false;
    n->col = j;
    n->valor = valor;
    n->prox = c;
    *pp = n;
    m->nnz++;
    return true;
}

double matriz_obter(const Matriz *m, size_t i, size_t j) {
    if (i >= m->linhas || j >= m->colunas) return 0.0;
    for (const Celula *c = m->linha[i]; c && c->col <= j; c = c->prox)
        if (c->col == j) return c->valor;
    return 0.0;
}

Matriz *matriz_transposta(const Matriz *m) {
    Matriz *t = matriz_nova(m->colunas, m->linhas);
    if (!t) return NULL;
    for (size_t i = 0; i < m->linhas; i++) {
        for (const Celula *c = m->linha[i]; c; c = c->prox) {
            if (!matriz_definir(t, c->col, i, c->valor)) {
                matriz_liberar(t);
                return NULL;
            }
        }
    }
    return t;
}

Matriz *matriz_somar(const Matriz *a, const Matriz *b) {
    if (a->linhas != b->linhas || a->colunas != b->colunas) return NULL;
    Matriz *r = matriz_nova(a->linhas, a->colunas);
    if (!r) return NULL;
    for (size_t i = 0; i < a->linhas; i++) {
        /* intercala as duas listas ordenadas */
        const Celula *x = a->linha[i], *y = b->linha[i];
        while (x || y) {
            size_t col;
            double v;
            if (x && (!y || x->col < y->col)) {
                col = x->col; v = x->valor; x = x->prox;
            } else if (y && (!x || y->col < x->col)) {
                col = y->col; v = y->valor; y = y->prox;
            } else {
                col = x->col; v = x->valor + y->valor; x = x->prox; y = y->prox;
            }
            if (!matriz_definir(r, i, col, v)) {   /* v == 0 nao cria celula */
                matriz_liberar(r);
                return NULL;
            }
        }
    }
    return r;
}

Matriz *matriz_multiplicar(const Matriz *a, const Matriz *b) {
    if (a->colunas != b->linhas) return NULL;
    Matriz *r = matriz_nova(a->linhas, b->colunas);
    double *acc = calloc(b->colunas ? b->colunas : 1, sizeof *acc);
    if (!r || !acc) {
        matriz_liberar(r);
        free(acc);
        return NULL;
    }
    for (size_t i = 0; i < a->linhas; i++) {
        /* linha i de r = soma de a[i][k] * (linha k de b) */
        for (const Celula *x = a->linha[i]; x; x = x->prox)
            for (const Celula *y = b->linha[x->col]; y; y = y->prox)
                acc[y->col] += x->valor * y->valor;
        for (size_t j = 0; j < b->colunas; j++) {
            if (acc[j] != 0.0 && !matriz_definir(r, i, j, acc[j])) {
                matriz_liberar(r);
                free(acc);
                return NULL;
            }
            acc[j] = 0.0;
        }
    }
    free(acc);
    return r;
}
