#include "kmp.h"
#include <stdlib.h>
#include <string.h>

/* Tabela de falha: pi[i] = maior borda propria de padrao[0..i]. */
static size_t *tabela_falha(const char *p, size_t m) {
    size_t *pi = malloc(m * sizeof *pi);
    if (!pi) return NULL;
    pi[0] = 0;
    for (size_t i = 1, k = 0; i < m; i++) {
        while (k > 0 && p[i] != p[k]) k = pi[k - 1];
        if (p[i] == p[k]) k++;
        pi[i] = k;
    }
    return pi;
}

static long varrer(const char *t, const char *p, int so_primeiro) {
    size_t m = strlen(p), n = strlen(t);
    if (m == 0) return 0;
    size_t *pi = tabela_falha(p, m);
    if (!pi) return so_primeiro ? -2 : -1;
    long achados = 0;
    for (size_t i = 0, k = 0; i < n; i++) {
        while (k > 0 && t[i] != p[k]) k = pi[k - 1];
        if (t[i] == p[k]) k++;
        if (k == m) {
            if (so_primeiro) { free(pi); return (long)(i + 1 - m); }
            achados++;
            k = pi[k - 1];
        }
    }
    free(pi);
    return so_primeiro ? -1 : achados;
}

long kmp_buscar(const char *texto, const char *padrao) { return varrer(texto, padrao, 1); }
long kmp_contar(const char *texto, const char *padrao) { return varrer(texto, padrao, 0); }
