#include "lcs.h"
#include <stdlib.h>
#include <string.h>

/* Tabela (la+1) x (lb+1) em um unico bloco; t[i][j] = LCS de a[0..i) e b[0..j). */
static size_t *montar(const char *a, const char *b, size_t la, size_t lb) {
    size_t w = lb + 1;
    size_t *t = calloc((la + 1) * w, sizeof *t);
    if (!t) return NULL;
    for (size_t i = 1; i <= la; i++)
        for (size_t j = 1; j <= lb; j++) {
            if (a[i - 1] == b[j - 1]) t[i * w + j] = t[(i - 1) * w + j - 1] + 1;
            else {
                size_t x = t[(i - 1) * w + j], y = t[i * w + j - 1];
                t[i * w + j] = x > y ? x : y;
            }
        }
    return t;
}

size_t lcs_tamanho(const char *a, const char *b) {
    size_t la = strlen(a), lb = strlen(b);
    size_t *t = montar(a, b, la, lb);
    if (!t) return (size_t)-1;
    size_t r = t[la * (lb + 1) + lb];
    free(t);
    return r;
}

char *lcs_string(const char *a, const char *b) {
    size_t la = strlen(a), lb = strlen(b), w = lb + 1;
    size_t *t = montar(a, b, la, lb);
    if (!t) return NULL;
    size_t len = t[la * w + lb];
    char *out = malloc(len + 1);
    if (!out) { free(t); return NULL; }
    out[len] = '\0';
    /* reconstroi caminhando de tras para frente */
    size_t i = la, j = lb, k = len;
    while (i > 0 && j > 0) {
        if (a[i - 1] == b[j - 1]) { out[--k] = a[i - 1]; i--; j--; }
        else if (t[(i - 1) * w + j] >= t[i * w + j - 1]) i--;
        else j--;
    }
    free(t);
    return out;
}
