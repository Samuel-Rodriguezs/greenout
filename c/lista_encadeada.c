#include "lista_encadeada.h"

#include <stdlib.h>

static No *novo_no(int valor, No *prox) {
    No *n = malloc(sizeof *n);
    if (n == NULL) {
        return NULL;
    }
    n->valor = valor;
    n->prox = prox;
    return n;
}

No *lista_inserir_inicio(No *lista, int valor) {
    No *n = novo_no(valor, lista);
    return n != NULL ? n : lista;
}

No *lista_inserir_fim(No *lista, int valor) {
    No *n = novo_no(valor, NULL);
    if (n == NULL) {
        return lista;
    }
    if (lista == NULL) {
        return n;
    }
    No *cur = lista;
    while (cur->prox != NULL) {
        cur = cur->prox;
    }
    cur->prox = n;
    return lista;
}

No *lista_remover(No *lista, int valor, bool *removido) {
    bool achou = false;
    No *ant = NULL;
    No *cur = lista;
    while (cur != NULL && cur->valor != valor) {
        ant = cur;
        cur = cur->prox;
    }
    if (cur != NULL) {
        achou = true;
        if (ant == NULL) {
            lista = cur->prox;
        } else {
            ant->prox = cur->prox;
        }
        free(cur);
    }
    if (removido != NULL) {
        *removido = achou;
    }
    return lista;
}

bool lista_contem(const No *lista, int valor) {
    for (; lista != NULL; lista = lista->prox) {
        if (lista->valor == valor) {
            return true;
        }
    }
    return false;
}

size_t lista_tamanho(const No *lista) {
    size_t n = 0;
    for (; lista != NULL; lista = lista->prox) {
        n++;
    }
    return n;
}

No *lista_inverter(No *lista) {
    No *ant = NULL;
    while (lista != NULL) {
        No *prox = lista->prox;
        lista->prox = ant;
        ant = lista;
        lista = prox;
    }
    return ant;
}

void lista_liberar(No *lista) {
    while (lista != NULL) {
        No *prox = lista->prox;
        free(lista);
        lista = prox;
    }
}
