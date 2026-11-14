#include <assert.h>
#include <stdio.h>
#include "vetor.h"

int main(void) {
    Vetor *v = vetor_novo();
    int x;
    assert(vetor_tam(v) == 0);
    assert(!vetor_obter(v, 0, &x));
    assert(!vetor_remover(v, 0, &x));
    for (int i = 0; i < 1000; i++) assert(vetor_adicionar(v, i));
    assert(vetor_tam(v) == 1000);
    assert(vetor_obter(v, 999, &x) && x == 999);
    assert(!vetor_obter(v, 1000, &x));
    assert(vetor_definir(v, 5, -7) && vetor_obter(v, 5, &x) && x == -7);
    assert(!vetor_definir(v, 1000, 1));
    assert(vetor_inserir(v, 0, 42) && vetor_obter(v, 0, &x) && x == 42);
    assert(vetor_obter(v, 1, &x) && x == 0);
    assert(vetor_inserir(v, vetor_tam(v), 99));
    assert(vetor_obter(v, vetor_tam(v) - 1, &x) && x == 99);
    assert(!vetor_inserir(v, vetor_tam(v) + 1, 1));
    assert(vetor_remover(v, 0, &x) && x == 42);
    assert(vetor_obter(v, 0, &x) && x == 0);
    assert(vetor_remover(v, vetor_tam(v) - 1, &x) && x == 99);
    vetor_limpar(v);
    assert(vetor_tam(v) == 0);
    assert(vetor_adicionar(v, 1));
    vetor_liberar(v);
    vetor_liberar(NULL);
    puts("vetor ok");
    return 0;
}
