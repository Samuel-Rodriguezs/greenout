#include "vetor.h"
#include <stdlib.h>
#include <string.h>

Vetor *vetor_novo(void) {
    Vetor *v = malloc(sizeof *v);
    if (!v) return NULL;
    v->dados = NULL;
    v->tam = 0;
    v->cap = 0;
    return v;
}

void vetor_liberar(Vetor *v) {
    if (!v) return;
    free(v->dados);
    free(v);
}

size_t vetor_tam(const Vetor *v) { return v->tam; }

/* Garante espaco para mais um elemento, dobrando a capacidade. */
static bool garantir(Vetor *v) {
    if (v->tam < v->cap) return true;
    size_t nova = v->cap ? v->cap * 2 : 4;
    int *p = realloc(v->dados, nova * sizeof *p);
    if (!p) return false;
    v->dados = p;
    v->cap = nova;
    return true;
}

bool vetor_adicionar(Vetor *v, int x) {
    if (!garantir(v)) return false;
    v->dados[v->tam++] = x;
    return true;
}

bool vetor_obter(const Vetor *v, size_t i, int *saida) {
    if (i >= v->tam) return false;
    if (saida) *saida = v->dados[i];
    return true;
}

bool vetor_definir(Vetor *v, size_t i, int x) {
    if (i >= v->tam) return false;
    v->dados[i] = x;
    return true;
}

bool vetor_inserir(Vetor *v, size_t i, int x) {
    if (i > v->tam) return false;
    if (!garantir(v)) return false;
    memmove(v->dados + i + 1, v->dados + i, (v->tam - i) * sizeof(int));
    v->dados[i] = x;
    v->tam++;
    return true;
}

bool vetor_remover(Vetor *v, size_t i, int *saida) {
    if (i >= v->tam) return false;
    if (saida) *saida = v->dados[i];
    memmove(v->dados + i, v->dados + i + 1, (v->tam - i - 1) * sizeof(int));
    v->tam--;
    return true;
}

void vetor_limpar(Vetor *v) { v->tam = 0; }
