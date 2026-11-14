#include "tabela_hash.h"
#include <stdlib.h>
#include <string.h>

#define BALDES_INICIAIS 8

/* djb2 */
static size_t hash(const char *s) {
    size_t h = 5381;
    for (; *s; s++) h = h * 33 + (unsigned char)*s;
    return h;
}

Tabela *tabela_nova(void) {
    Tabela *t = malloc(sizeof *t);
    if (!t) return NULL;
    t->baldes = calloc(BALDES_INICIAIS, sizeof *t->baldes);
    if (!t->baldes) {
        free(t);
        return NULL;
    }
    t->nbaldes = BALDES_INICIAIS;
    t->tam = 0;
    return t;
}

void tabela_liberar(Tabela *t) {
    if (!t) return;
    for (size_t i = 0; i < t->nbaldes; i++) {
        Entrada *e = t->baldes[i];
        while (e) {
            Entrada *p = e->prox;
            free(e->chave);
            free(e);
            e = p;
        }
    }
    free(t->baldes);
    free(t);
}

size_t tabela_tam(const Tabela *t) { return t->tam; }

/* Dobra o numero de baldes reaproveitando os nos existentes. */
static bool redimensionar(Tabela *t) {
    size_t novo = t->nbaldes * 2;
    Entrada **nb = calloc(novo, sizeof *nb);
    if (!nb) return false;
    for (size_t i = 0; i < t->nbaldes; i++) {
        Entrada *e = t->baldes[i];
        while (e) {
            Entrada *p = e->prox;
            size_t idx = hash(e->chave) % novo;
            e->prox = nb[idx];
            nb[idx] = e;
            e = p;
        }
    }
    free(t->baldes);
    t->baldes = nb;
    t->nbaldes = novo;
    return true;
}

bool tabela_inserir(Tabela *t, const char *chave, int valor) {
    size_t idx = hash(chave) % t->nbaldes;
    for (Entrada *e = t->baldes[idx]; e; e = e->prox) {
        if (strcmp(e->chave, chave) == 0) {
            e->valor = valor;
            return true;
        }
    }
    if ((t->tam + 1) * 4 > t->nbaldes * 3) {
        if (!redimensionar(t)) return false;
        idx = hash(chave) % t->nbaldes;
    }
    Entrada *e = malloc(sizeof *e);
    if (!e) return false;
    size_t n = strlen(chave) + 1;
    e->chave = malloc(n);
    if (!e->chave) {
        free(e);
        return false;
    }
    memcpy(e->chave, chave, n);
    e->valor = valor;
    e->prox = t->baldes[idx];
    t->baldes[idx] = e;
    t->tam++;
    return true;
}

bool tabela_buscar(const Tabela *t, const char *chave, int *saida) {
    for (Entrada *e = t->baldes[hash(chave) % t->nbaldes]; e; e = e->prox) {
        if (strcmp(e->chave, chave) == 0) {
            if (saida) *saida = e->valor;
            return true;
        }
    }
    return false;
}

bool tabela_remover(Tabela *t, const char *chave) {
    Entrada **pp = &t->baldes[hash(chave) % t->nbaldes];
    while (*pp) {
        Entrada *e = *pp;
        if (strcmp(e->chave, chave) == 0) {
            *pp = e->prox;
            free(e->chave);
            free(e);
            t->tam--;
            return true;
        }
        pp = &e->prox;
    }
    return false;
}
