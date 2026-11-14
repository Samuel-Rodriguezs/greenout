#include "vida.h"
#include <stdlib.h>
#include <string.h>

static int mod(int a, int m) { return ((a % m) + m) % m; }

Vida *vida_criar(int lin, int col) {
    if (lin <= 0 || col <= 0) return NULL;
    Vida *v = malloc(sizeof *v);
    if (!v) return NULL;
    v->lin = lin; v->col = col;
    v->cel = calloc((size_t)lin * col, 1);
    if (!v->cel) { free(v); return NULL; }
    return v;
}

void vida_liberar(Vida *v) {
    if (!v) return;
    free(v->cel);
    free(v);
}

void vida_set(Vida *v, int l, int c, int viva) {
    v->cel[mod(l, v->lin) * v->col + mod(c, v->col)] = viva ? 1 : 0;
}

int vida_get(const Vida *v, int l, int c) {
    return v->cel[mod(l, v->lin) * v->col + mod(c, v->col)];
}

static int vizinhos(const Vida *v, int l, int c) {
    int n = 0;
    for (int dl = -1; dl <= 1; dl++)
        for (int dc = -1; dc <= 1; dc++)
            if (dl || dc) n += vida_get(v, l + dl, c + dc);
    return n;
}

void vida_passo(Vida *v) {
    size_t tam = (size_t)v->lin * v->col;
    unsigned char *prox = malloc(tam);
    if (!prox) return;
    for (int l = 0; l < v->lin; l++)
        for (int c = 0; c < v->col; c++) {
            int n = vizinhos(v, l, c);
            int viva = vida_get(v, l, c);
            prox[l * v->col + c] = viva ? (n == 2 || n == 3) : (n == 3);
        }
    memcpy(v->cel, prox, tam);
    free(prox);
}

int vida_populacao(const Vida *v) {
    int n = 0;
    for (size_t i = 0; i < (size_t)v->lin * v->col; i++) n += v->cel[i];
    return n;
}
