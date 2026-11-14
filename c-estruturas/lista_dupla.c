#include "lista_dupla.h"
#include <stdlib.h>

Lista *lista_nova(void) {
    Lista *l = malloc(sizeof *l);
    if (!l) return NULL;
    l->cabeca = l->cauda = NULL;
    l->tam = 0;
    return l;
}

void lista_liberar(Lista *l) {
    if (!l) return;
    No *n = l->cabeca;
    while (n) {
        No *p = n->prox;
        free(n);
        n = p;
    }
    free(l);
}

size_t lista_tam(const Lista *l) { return l->tam; }

static No *novo_no(int x) {
    No *n = malloc(sizeof *n);
    if (!n) return NULL;
    n->valor = x;
    n->ant = n->prox = NULL;
    return n;
}

bool lista_push_frente(Lista *l, int x) {
    No *n = novo_no(x);
    if (!n) return false;
    n->prox = l->cabeca;
    if (l->cabeca) l->cabeca->ant = n; else l->cauda = n;
    l->cabeca = n;
    l->tam++;
    return true;
}

bool lista_push_tras(Lista *l, int x) {
    No *n = novo_no(x);
    if (!n) return false;
    n->ant = l->cauda;
    if (l->cauda) l->cauda->prox = n; else l->cabeca = n;
    l->cauda = n;
    l->tam++;
    return true;
}

/* Desliga o no da lista e o libera. */
static void desligar(Lista *l, No *n) {
    if (n->ant) n->ant->prox = n->prox; else l->cabeca = n->prox;
    if (n->prox) n->prox->ant = n->ant; else l->cauda = n->ant;
    free(n);
    l->tam--;
}

bool lista_pop_frente(Lista *l, int *saida) {
    if (!l->cabeca) return false;
    if (saida) *saida = l->cabeca->valor;
    desligar(l, l->cabeca);
    return true;
}

bool lista_pop_tras(Lista *l, int *saida) {
    if (!l->cauda) return false;
    if (saida) *saida = l->cauda->valor;
    desligar(l, l->cauda);
    return true;
}

/* Percorre a partir do lado mais proximo do indice. */
static No *no_em(const Lista *l, size_t i) {
    No *n;
    if (i < l->tam / 2) {
        n = l->cabeca;
        while (i--) n = n->prox;
    } else {
        n = l->cauda;
        for (size_t k = l->tam - 1; k > i; k--) n = n->ant;
    }
    return n;
}

bool lista_obter(const Lista *l, size_t i, int *saida) {
    if (i >= l->tam) return false;
    if (saida) *saida = no_em(l, i)->valor;
    return true;
}

bool lista_inserir(Lista *l, size_t i, int x) {
    if (i > l->tam) return false;
    if (i == 0) return lista_push_frente(l, x);
    if (i == l->tam) return lista_push_tras(l, x);
    No *n = novo_no(x);
    if (!n) return false;
    No *pos = no_em(l, i);
    n->prox = pos;
    n->ant = pos->ant;
    pos->ant->prox = n;
    pos->ant = n;
    l->tam++;
    return true;
}

bool lista_remover_valor(Lista *l, int x) {
    for (No *n = l->cabeca; n; n = n->prox) {
        if (n->valor == x) {
            desligar(l, n);
            return true;
        }
    }
    return false;
}

void lista_inverter(Lista *l) {
    No *n = l->cabeca;
    while (n) {
        No *p = n->prox;
        n->prox = n->ant;
        n->ant = p;
        n = p;
    }
    No *t = l->cabeca;
    l->cabeca = l->cauda;
    l->cauda = t;
}
