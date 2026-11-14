#include "heap.h"
#include <stdlib.h>
#include <string.h>

Heap *heap_novo(void) {
    Heap *h = malloc(sizeof *h);
    if (!h) return NULL;
    h->dados = NULL;
    h->tam = h->cap = 0;
    return h;
}

void heap_liberar(Heap *h) {
    if (!h) return;
    free(h->dados);
    free(h);
}

size_t heap_tam(const Heap *h) { return h->tam; }

static void trocar(int *a, int *b) {
    int t = *a;
    *a = *b;
    *b = t;
}

static void subir(Heap *h, size_t i) {
    while (i > 0) {
        size_t pai = (i - 1) / 2;
        if (h->dados[pai] <= h->dados[i]) break;
        trocar(&h->dados[pai], &h->dados[i]);
        i = pai;
    }
}

static void descer(Heap *h, size_t i) {
    for (;;) {
        size_t e = 2 * i + 1, d = e + 1, menor = i;
        if (e < h->tam && h->dados[e] < h->dados[menor]) menor = e;
        if (d < h->tam && h->dados[d] < h->dados[menor]) menor = d;
        if (menor == i) return;
        trocar(&h->dados[i], &h->dados[menor]);
        i = menor;
    }
}

bool heap_inserir(Heap *h, int x) {
    if (h->tam == h->cap) {
        size_t nova = h->cap ? h->cap * 2 : 8;
        int *p = realloc(h->dados, nova * sizeof *p);
        if (!p) return false;
        h->dados = p;
        h->cap = nova;
    }
    h->dados[h->tam] = x;
    subir(h, h->tam++);
    return true;
}

bool heap_topo(const Heap *h, int *saida) {
    if (h->tam == 0) return false;
    if (saida) *saida = h->dados[0];
    return true;
}

bool heap_extrair(Heap *h, int *saida) {
    if (h->tam == 0) return false;
    if (saida) *saida = h->dados[0];
    h->dados[0] = h->dados[--h->tam];
    if (h->tam > 0) descer(h, 0);
    return true;
}

Heap *heap_de_vetor(const int *v, size_t n) {
    Heap *h = heap_novo();
    if (!h) return NULL;
    if (n > 0) {
        h->dados = malloc(n * sizeof(int));
        if (!h->dados) {
            free(h);
            return NULL;
        }
        memcpy(h->dados, v, n * sizeof(int));
        h->tam = h->cap = n;
        for (size_t i = n / 2; i-- > 0;) descer(h, i);
    }
    return h;
}
