#include <assert.h>
#include <stdio.h>
#include "heap.h"

int main(void) {
    Heap *h = heap_novo();
    int x;
    assert(heap_tam(h) == 0 && !heap_topo(h, &x) && !heap_extrair(h, &x));
    /* sequencia pseudo-aleatoria deterministica, com repetidos e negativos */
    unsigned s = 12345;
    for (int i = 0; i < 500; i++) {
        s = s * 1103515245u + 12345u;
        assert(heap_inserir(h, (int)((s >> 16) % 201) - 100));
    }
    assert(heap_tam(h) == 500);
    int ant = -1000;
    for (int i = 0; i < 500; i++) {
        assert(heap_topo(h, &x));
        int y;
        assert(heap_extrair(h, &y) && x == y && y >= ant);
        ant = y;
    }
    assert(heap_tam(h) == 0 && !heap_extrair(h, &x));
    assert(heap_inserir(h, 1));                 /* reutilizavel apos esvaziar */
    assert(heap_extrair(h, &x) && x == 1);
    heap_liberar(h);

    int v[] = {9, 4, 7, 1, 8, 2, 2, 6};
    h = heap_de_vetor(v, 8);
    int esperado[] = {1, 2, 2, 4, 6, 7, 8, 9};
    for (int i = 0; i < 8; i++) assert(heap_extrair(h, &x) && x == esperado[i]);
    heap_liberar(h);
    h = heap_de_vetor(NULL, 0);                 /* vazio */
    assert(h && heap_tam(h) == 0);
    heap_liberar(h);
    heap_liberar(NULL);
    puts("heap ok");
    return 0;
}
