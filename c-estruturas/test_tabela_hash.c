#include <assert.h>
#include <stdio.h>
#include "tabela_hash.h"

int main(void) {
    Tabela *t = tabela_nova();
    int x;
    assert(tabela_tam(t) == 0);
    assert(!tabela_buscar(t, "a", &x));
    assert(!tabela_remover(t, "a"));
    assert(tabela_inserir(t, "a", 1) && tabela_inserir(t, "b", 2));
    assert(tabela_inserir(t, "", 77));          /* chave vazia */
    assert(tabela_buscar(t, "", &x) && x == 77);
    assert(tabela_inserir(t, "a", 10));         /* atualiza */
    assert(tabela_tam(t) == 3);
    assert(tabela_buscar(t, "a", &x) && x == 10);
    assert(!tabela_buscar(t, "c", &x));

    char chave[32];
    for (int i = 0; i < 2000; i++) {            /* forca varios redimensionamentos/colisoes */
        snprintf(chave, sizeof chave, "chave%d", i);
        assert(tabela_inserir(t, chave, i));
    }
    assert(tabela_tam(t) == 2003);
    for (int i = 0; i < 2000; i++) {
        snprintf(chave, sizeof chave, "chave%d", i);
        assert(tabela_buscar(t, chave, &x) && x == i);
    }
    for (int i = 0; i < 2000; i += 2) {
        snprintf(chave, sizeof chave, "chave%d", i);
        assert(tabela_remover(t, chave));
        assert(!tabela_remover(t, chave));
    }
    assert(tabela_tam(t) == 1003);
    assert(tabela_buscar(t, "chave1", &x) && x == 1);
    assert(!tabela_buscar(t, "chave0", &x));
    tabela_liberar(t);
    tabela_liberar(NULL);
    puts("tabela_hash ok");
    return 0;
}
