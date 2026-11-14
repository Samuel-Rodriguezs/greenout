#include "pilha.h"

void pilha_init(Pilha *p) {
    p->topo = 0;
}

bool pilha_vazia(const Pilha *p) {
    return p->topo == 0;
}

bool pilha_cheia(const Pilha *p) {
    return p->topo == PILHA_CAPACIDADE;
}

size_t pilha_tamanho(const Pilha *p) {
    return p->topo;
}

bool pilha_push(Pilha *p, int valor) {
    if (pilha_cheia(p)) {
        return false;
    }
    p->dados[p->topo++] = valor;
    return true;
}

bool pilha_pop(Pilha *p, int *valor) {
    if (pilha_vazia(p)) {
        return false;
    }
    *valor = p->dados[--p->topo];
    return true;
}

bool pilha_topo(const Pilha *p, int *valor) {
    if (pilha_vazia(p)) {
        return false;
    }
    *valor = p->dados[p->topo - 1];
    return true;
}
