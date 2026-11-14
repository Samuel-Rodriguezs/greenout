#include "matriz.h"
#include <stdint.h>
#include <stdlib.h>

Matriz *matriz_criar(size_t lin, size_t col) {
    if (lin == 0 || col == 0) return NULL;
    if (lin > SIZE_MAX / col / sizeof(double)) return NULL;   /* overflow */
    Matriz *m = malloc(sizeof *m);
    if (!m) return NULL;
    m->dados = calloc(lin * col, sizeof *m->dados);
    if (!m->dados) { free(m); return NULL; }
    m->lin = lin;
    m->col = col;
    return m;
}

void matriz_liberar(Matriz *m) {
    if (!m) return;
    free(m->dados);
    free(m);
}

double matriz_get(const Matriz *m, size_t i, size_t j) { return m->dados[i * m->col + j]; }
void matriz_set(Matriz *m, size_t i, size_t j, double v) { m->dados[i * m->col + j] = v; }

Matriz *matriz_multiplicar(const Matriz *a, const Matriz *b) {
    if (a->col != b->lin) return NULL;
    Matriz *r = matriz_criar(a->lin, b->col);
    if (!r) return NULL;
    /* ordem i-k-j: percorre b e r linha a linha (melhor uso de cache) */
    for (size_t i = 0; i < a->lin; i++)
        for (size_t k = 0; k < a->col; k++) {
            double aik = a->dados[i * a->col + k];
            for (size_t j = 0; j < b->col; j++)
                r->dados[i * r->col + j] += aik * b->dados[k * b->col + j];
        }
    return r;
}

Matriz *matriz_transposta(const Matriz *m) {
    Matriz *t = matriz_criar(m->col, m->lin);
    if (!t) return NULL;
    for (size_t i = 0; i < m->lin; i++)
        for (size_t j = 0; j < m->col; j++)
            t->dados[j * t->col + i] = m->dados[i * m->col + j];
    return t;
}
