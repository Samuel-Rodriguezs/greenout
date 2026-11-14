#include "substituicao.h"

#include <stdlib.h>

/* busca linear da pagina nos quadros ocupados; -1 se ausente */
static long achar(const int *pag, size_t ocupados, int p) {
    for (size_t i = 0; i < ocupados; i++)
        if (pag[i] == p) return (long)i;
    return -1;
}

int subst_fifo(const int *refs, size_t n, size_t quadros) {
    if (quadros == 0) return -1;
    int *pag = malloc(quadros * sizeof *pag);
    if (!pag) return -1;
    size_t ocup = 0, proximo = 0;
    int faltas = 0;
    for (size_t i = 0; i < n; i++) {
        if (achar(pag, ocup, refs[i]) >= 0) continue;
        faltas++;
        if (ocup < quadros) {
            pag[ocup++] = refs[i];
        } else { /* vitima = a pagina mais antiga */
            pag[proximo] = refs[i];
            proximo = (proximo + 1) % quadros;
        }
    }
    free(pag);
    return faltas;
}

int subst_lru(const int *refs, size_t n, size_t quadros) {
    if (quadros == 0) return -1;
    int *pag = malloc(quadros * sizeof *pag);
    size_t *uso = malloc(quadros * sizeof *uso);
    if (!pag || !uso) {
        free(pag);
        free(uso);
        return -1;
    }
    size_t ocup = 0;
    int faltas = 0;
    for (size_t i = 0; i < n; i++) {
        long k = achar(pag, ocup, refs[i]);
        if (k >= 0) {
            uso[k] = i;
            continue;
        }
        faltas++;
        if (ocup < quadros) {
            pag[ocup] = refs[i];
            uso[ocup++] = i;
        } else {
            size_t v = 0;
            for (size_t j = 1; j < quadros; j++)
                if (uso[j] < uso[v]) v = j;
            pag[v] = refs[i];
            uso[v] = i;
        }
    }
    free(pag);
    free(uso);
    return faltas;
}

int subst_clock(const int *refs, size_t n, size_t quadros) {
    if (quadros == 0) return -1;
    int *pag = malloc(quadros * sizeof *pag);
    unsigned char *ref = calloc(quadros, 1);
    if (!pag || !ref) {
        free(pag);
        free(ref);
        return -1;
    }
    size_t ocup = 0, mao = 0;
    int faltas = 0;
    for (size_t i = 0; i < n; i++) {
        long k = achar(pag, ocup, refs[i]);
        if (k >= 0) {
            ref[k] = 1;
            continue;
        }
        faltas++;
        if (ocup < quadros) { /* fase de preenchimento: a mao acompanha */
            pag[ocup] = refs[i];
            ref[ocup] = 1;
            ocup++;
            mao = ocup % quadros;
            continue;
        }
        while (ref[mao]) { /* da segunda chance */
            ref[mao] = 0;
            mao = (mao + 1) % quadros;
        }
        pag[mao] = refs[i];
        ref[mao] = 1;
        mao = (mao + 1) % quadros;
    }
    free(pag);
    free(ref);
    return faltas;
}

int subst_otimo(const int *refs, size_t n, size_t quadros) {
    if (quadros == 0) return -1;
    int *pag = malloc(quadros * sizeof *pag);
    if (!pag) return -1;
    size_t ocup = 0;
    int faltas = 0;
    for (size_t i = 0; i < n; i++) {
        if (achar(pag, ocup, refs[i]) >= 0) continue;
        faltas++;
        if (ocup < quadros) {
            pag[ocup++] = refs[i];
            continue;
        }
        /* vitima: a pagina cujo proximo uso e o mais distante (ou nunca) */
        size_t v = 0, melhor = 0;
        for (size_t j = 0; j < quadros; j++) {
            size_t prox = n; /* n = nunca mais usada */
            for (size_t k = i + 1; k < n; k++)
                if (refs[k] == pag[j]) {
                    prox = k;
                    break;
                }
            if (prox > melhor) {
                melhor = prox;
                v = j;
            }
        }
        pag[v] = refs[i];
    }
    free(pag);
    return faltas;
}
