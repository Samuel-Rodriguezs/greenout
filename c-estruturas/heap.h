#ifndef HEAP_H
#define HEAP_H
#include <stdbool.h>
#include <stddef.h>

/* Heap binario de minimo (int) sobre vetor dinamico. */
typedef struct {
    int *dados;
    size_t tam;
    size_t cap;
} Heap;

Heap *heap_novo(void);
void heap_liberar(Heap *h);
size_t heap_tam(const Heap *h);
bool heap_inserir(Heap *h, int x);
bool heap_topo(const Heap *h, int *saida);        /* menor elemento */
bool heap_extrair(Heap *h, int *saida);           /* remove o menor */
/* Constroi um heap em O(n) a partir de um vetor (heapify). */
Heap *heap_de_vetor(const int *v, size_t n);

#endif
