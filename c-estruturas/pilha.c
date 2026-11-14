#include "pilha.h"
#include <stdlib.h>

Pilha *pilha_nova(void) {
    Pilha *p = malloc(sizeof *p);
    if (!p) return NULL;
    p->topo = NULL;
    p->tam = 0;
    return p;
}

void pilha_liberar(Pilha *p) {
    if (!p) return;
    while (p->topo) {
        NoPilha *n = p->topo;
        p->topo = n->abaixo;
        free(n);
    }
    free(p);
}

bool pilha_empilhar(Pilha *p, int x) {
    NoPilha *n = malloc(sizeof *n);
    if (!n) return false;
    n->valor = x;
    n->abaixo = p->topo;
    p->topo = n;
    p->tam++;
    return true;
}

bool pilha_desempilhar(Pilha *p, int *saida) {
    if (!p->topo) return false;
    NoPilha *n = p->topo;
    if (saida) *saida = n->valor;
    p->topo = n->abaixo;
    free(n);
    p->tam--;
    return true;
}

bool pilha_topo(const Pilha *p, int *saida) {
    if (!p->topo) return false;
    if (saida) *saida = p->topo->valor;
    return true;
}

bool pilha_vazia(const Pilha *p) { return p->topo == NULL; }
size_t pilha_tam(const Pilha *p) { return p->tam; }
