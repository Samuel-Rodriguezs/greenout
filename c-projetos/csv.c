#include "csv.h"
#include <stdlib.h>
#include <string.h>

void csv_free(Csv *c) {
    if (!c) return;
    for (size_t i = 0; i < c->n_linhas; i++) {
        for (size_t j = 0; j < c->n_cols[i]; j++) free(c->celulas[i][j]);
        free(c->celulas[i]);
    }
    free(c->celulas);
    free(c->n_cols);
    free(c);
}

/* Acrescenta a celula (posse transferida) a ultima linha. */
static int add_celula(Csv *c, char *cel) {
    size_t l = c->n_linhas - 1;
    char **nv = realloc(c->celulas[l], (c->n_cols[l] + 1) * sizeof *nv);
    if (!nv) { free(cel); return -1; }
    c->celulas[l] = nv;
    nv[c->n_cols[l]++] = cel;
    return 0;
}

static int nova_linha(Csv *c) {
    char ***cel = realloc(c->celulas, (c->n_linhas + 1) * sizeof *cel);
    if (!cel) return -1;
    c->celulas = cel;
    size_t *nc = realloc(c->n_cols, (c->n_linhas + 1) * sizeof *nc);
    if (!nc) return -1;
    c->n_cols = nc;
    cel[c->n_linhas] = NULL;
    nc[c->n_linhas++] = 0;
    return 0;
}

Csv *csv_parse(const char *s) {
    Csv *c = calloc(1, sizeof *c);
    if (!c) return NULL;
    if (*s == '\0') return c;
    if (nova_linha(c)) goto erro;
    while (1) {
        /* le um campo */
        size_t cap = 16, n = 0;
        char *campo = malloc(cap);
        if (!campo) goto erro;
        int aspas = *s == '"';
        if (aspas) s++;
        while (1) {
            if (n + 2 > cap) {
                char *t = realloc(campo, cap *= 2);
                if (!t) { free(campo); goto erro; }
                campo = t;
            }
            if (aspas) {
                if (*s == '\0') { free(campo); goto erro; } /* nao fechou */
                if (*s == '"') {
                    if (s[1] == '"') { campo[n++] = '"'; s += 2; continue; }
                    s++; aspas = 0; continue;
                }
                campo[n++] = *s++;
            } else {
                if (*s == ',' || *s == '\n' || *s == '\r' || *s == '\0') break;
                campo[n++] = *s++;
            }
        }
        campo[n] = 0;
        if (add_celula(c, campo)) goto erro;
        if (*s == ',') { s++; continue; }
        if (*s == '\r') s++;
        if (*s == '\n') s++;
        if (*s == '\0') break;
        if (nova_linha(c)) goto erro;
    }
    return c;
erro:
    csv_free(c);
    return NULL;
}
