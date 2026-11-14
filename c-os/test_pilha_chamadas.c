#include <assert.h>
#include <stdio.h>
#include <string.h>

#include "pilha_chamadas.h"

/* fatorial recursivo "executado" na pilha simulada: cada nivel guarda n */
static int64_t fat(PilhaChamadas *p, int64_t n, int64_t ra) {
    assert(pc_chamar(p, "fat", ra, 1) == 0);
    assert(pc_local_set(p, 0, n) == 0);
    int64_t r = 1;
    if (n > 1) r = n * fat(p, n - 1, 100 + n);
    int64_t v;
    assert(pc_local_get(p, 0, &v) == 0 && v == n); /* local preservada */
    assert(pc_retornar(p, NULL) == 0);
    return r;
}

int main(void) {
    assert(pc_criar(1) == NULL);
    PilhaChamadas *p = pc_criar(20);
    int64_t v = -1;
    assert(p && pc_profundidade(p) == 0 && pc_palavras_usadas(p) == 0);

    /* sem frame: retornar/acessar falha; backtrace vazio */
    assert(pc_retornar(p, &v) == -1);
    assert(pc_local_set(p, 0, 1) == -1 && pc_local_get(p, 0, &v) == -1);
    char buf[128] = "x";
    assert(pc_backtrace(p, buf, sizeof buf) == 0 && buf[0] == '\0');

    /* main -> a -> b, com tamanhos de frame diferentes */
    assert(pc_chamar(p, "main", 0, 2) == 0);   /* 4 palavras */
    assert(pc_chamar(p, "a", 0x10, 1) == 0);   /* 3 palavras */
    assert(pc_chamar(p, "b", 0x20, 0) == 0);   /* 2 palavras */
    assert(pc_profundidade(p) == 3 && pc_palavras_usadas(p) == 9);
    assert(pc_local_set(p, 0, 5) == -1);       /* b nao tem locais */

    assert(pc_backtrace(p, buf, sizeof buf) > 0);
    assert(strcmp(buf, "#0 b ret=32\n#1 a ret=16\n#2 main ret=0\n") == 0);

    /* backtrace truncado: sempre termina em '\0' e informa o tamanho total */
    char pequeno[8];
    size_t total = pc_backtrace(p, pequeno, sizeof pequeno);
    assert(total == strlen("#0 b ret=32\n#1 a ret=16\n#2 main ret=0\n"));
    assert(strlen(pequeno) == 7 && strncmp(pequeno, "#0 b re", 7) == 0);
    assert(pc_backtrace(p, NULL, 0) == total);

    /* retornos restauram o frame do chamador */
    assert(pc_retornar(p, &v) == 0 && v == 0x20);
    assert(pc_local_set(p, 0, 77) == 0);       /* agora e o frame de a */
    assert(pc_retornar(p, &v) == 0 && v == 0x10);
    assert(pc_local_set(p, 1, 9) == 0 && pc_local_set(p, 2, 9) == -1);
    assert(pc_local_get(p, 1, &v) == 0 && v == 9);
    assert(pc_retornar(p, &v) == 0 && v == 0);
    assert(pc_profundidade(p) == 0 && pc_palavras_usadas(p) == 0);

    /* locais de um frame novo comecam zeradas mesmo reutilizando memoria */
    assert(pc_chamar(p, "c", 1, 2) == 0 && pc_local_get(p, 0, &v) == 0 && v == 0);
    assert(pc_retornar(p, NULL) == 0);

    /* estouro: 20 palavras, frames de 5 -> 4 cabem, o quinto falha intacto */
    for (int i = 0; i < 4; i++) assert(pc_chamar(p, "r", i, 3) == 0);
    assert(pc_chamar(p, "r", 4, 3) == -1);
    assert(pc_profundidade(p) == 4 && pc_palavras_usadas(p) == 20);
    assert(pc_chamar(p, "r", 4, 0) == -1);     /* nem 2 palavras sobram */
    for (int i = 3; i >= 0; i--) assert(pc_retornar(p, &v) == 0 && v == i);
    assert(pc_chamar(p, "enorme", 0, 1000) == -1);
    pc_destruir(p);

    /* recursao real: 10! = 3628800 usa 10 frames de 3 palavras */
    PilhaChamadas *q = pc_criar(30);
    assert(fat(q, 10, 0) == 3628800);
    assert(pc_profundidade(q) == 0);
    pc_destruir(q);
    q = pc_criar(29); /* 1 palavra a menos: o decimo frame nao cabe */
    PilhaChamadas *r = pc_criar(2);
    assert(r && pc_chamar(r, "z", 5, 0) == 0 && pc_chamar(r, "z", 5, 0) == -1);
    pc_destruir(r);
    int ok = 1;
    for (int i = 0; i < 10 && ok; i++) ok = pc_chamar(q, "f", i, 1) == 0;
    assert(!ok);
    pc_destruir(q);
    pc_destruir(NULL);

    puts("test_pilha_chamadas ok");
    return 0;
}
