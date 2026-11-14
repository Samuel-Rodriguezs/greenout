#include "disco_sched.h"

#include <stdlib.h>
#include <string.h>

static int valido(int cabeca, const int *r, size_t n, int max_cil) {
    if (max_cil < 0 || cabeca < 0 || cabeca > max_cil) return 0;
    for (size_t i = 0; i < n; i++)
        if (r[i] < 0 || r[i] > max_cil) return 0;
    return 1;
}

static long dist(int a, int b) { return a > b ? a - b : b - a; }

static int cmp_asc(const void *a, const void *b) {
    return (*(const int *)a > *(const int *)b) - (*(const int *)a < *(const int *)b);
}

long disco_fcfs(int cabeca, const int *reqs, size_t n, int max_cil, int *ordem) {
    if (!valido(cabeca, reqs, n, max_cil)) return -1;
    long total = 0;
    int pos = cabeca;
    for (size_t i = 0; i < n; i++) {
        total += dist(pos, reqs[i]);
        pos = reqs[i];
        if (ordem) ordem[i] = reqs[i];
    }
    return total;
}

long disco_sstf(int cabeca, const int *reqs, size_t n, int max_cil, int *ordem) {
    if (!valido(cabeca, reqs, n, max_cil)) return -1;
    unsigned char *feito = calloc(n ? n : 1, 1);
    if (!feito) return -1;
    long total = 0;
    int pos = cabeca;
    for (size_t k = 0; k < n; k++) {
        size_t melhor = n;
        for (size_t i = 0; i < n; i++) /* empate: o que aparece primeiro */
            if (!feito[i] && (melhor == n || dist(pos, reqs[i]) < dist(pos, reqs[melhor])))
                melhor = i;
        feito[melhor] = 1;
        total += dist(pos, reqs[melhor]);
        pos = reqs[melhor];
        if (ordem) ordem[k] = pos;
    }
    free(feito);
    return total;
}

/* Separa os pedidos em dois vetores ordenados: >= cabeca (cima) e < cabeca
 * (baixo). Pedidos na posicao da cabeca custam zero e ficam em `cima`. */
static int dividir(int cabeca, const int *r, size_t n, int **cima, size_t *nc,
                   int **baixo, size_t *nb) {
    *cima = malloc((n ? n : 1) * sizeof(int));
    *baixo = malloc((n ? n : 1) * sizeof(int));
    if (!*cima || !*baixo) {
        free(*cima);
        free(*baixo);
        return -1;
    }
    *nc = *nb = 0;
    for (size_t i = 0; i < n; i++) {
        if (r[i] >= cabeca) (*cima)[(*nc)++] = r[i];
        else (*baixo)[(*nb)++] = r[i];
    }
    qsort(*cima, *nc, sizeof(int), cmp_asc);
    qsort(*baixo, *nb, sizeof(int), cmp_asc);
    return 0;
}

long disco_scan(int cabeca, const int *reqs, size_t n, int max_cil, int sobe, int *ordem) {
    if (!valido(cabeca, reqs, n, max_cil)) return -1;
    if (n == 0) return 0;
    int *cima, *baixo;
    size_t nc, nb;
    if (dividir(cabeca, reqs, n, &cima, &nc, &baixo, &nb) < 0) return -1;
    long total;
    size_t k = 0;
    if (sobe) {
        for (size_t i = 0; i < nc; i++) if (ordem) ordem[k++] = cima[i];
        total = max_cil - cabeca;                      /* ate a borda superior */
        if (nb) {
            total += max_cil - baixo[0];               /* volta ate o menor pedido */
            for (size_t i = nb; i-- > 0;) if (ordem) ordem[k++] = baixo[i];
        }
    } else {
        /* descendo: primeiro os pedidos < cabeca, depois os >= (em ordem
         * decrescente a partir da cabeca nao ha: os iguais custam zero) */
        size_t iguais = 0;
        while (iguais < nc && cima[iguais] == cabeca) iguais++;
        for (size_t i = 0; i < iguais; i++) if (ordem) ordem[k++] = cima[i];
        for (size_t i = nb; i-- > 0;) if (ordem) ordem[k++] = baixo[i];
        total = cabeca;                                /* ate a borda 0 */
        if (nc > iguais) {
            total += cima[nc - 1];                     /* sobe ate o maior pedido */
            for (size_t i = iguais; i < nc; i++) if (ordem) ordem[k++] = cima[i];
        }
    }
    free(cima);
    free(baixo);
    return total;
}

long disco_cscan(int cabeca, const int *reqs, size_t n, int max_cil, int sobe, int *ordem) {
    if (!valido(cabeca, reqs, n, max_cil)) return -1;
    if (n == 0) return 0;
    int *cima, *baixo;
    size_t nc, nb;
    if (dividir(cabeca, reqs, n, &cima, &nc, &baixo, &nb) < 0) return -1;
    long total;
    size_t k = 0;
    if (sobe) {
        for (size_t i = 0; i < nc; i++) if (ordem) ordem[k++] = cima[i];
        total = max_cil - cabeca;
        if (nb) {
            total += max_cil;                          /* salto de retorno 199 -> 0 */
            total += baixo[nb - 1];                    /* sobe ate o maior pedido baixo */
            for (size_t i = 0; i < nb; i++) if (ordem) ordem[k++] = baixo[i];
        }
    } else {
        size_t iguais = 0;
        while (iguais < nc && cima[iguais] == cabeca) iguais++;
        for (size_t i = 0; i < iguais; i++) if (ordem) ordem[k++] = cima[i];
        for (size_t i = nb; i-- > 0;) if (ordem) ordem[k++] = baixo[i];
        total = cabeca;
        if (nc > iguais) {
            total += max_cil;                          /* salto 0 -> max */
            total += max_cil - cima[iguais];           /* desce ate o menor pedido alto */
            for (size_t i = nc; i-- > iguais;) if (ordem) ordem[k++] = cima[i];
        }
    }
    free(cima);
    free(baixo);
    return total;
}
