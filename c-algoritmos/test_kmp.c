#include <assert.h>
#include <stdio.h>
#include "kmp.h"

int main(void) {
    assert(kmp_buscar("abracadabra", "abra") == 0);
    assert(kmp_buscar("abracadabra", "cad") == 4);
    assert(kmp_buscar("abracadabra", "bra") == 1);
    assert(kmp_buscar("abracadabra", "xyz") == -1);
    assert(kmp_buscar("abc", "abcd") == -1);       /* padrao maior */
    assert(kmp_buscar("", "a") == -1);
    assert(kmp_buscar("abc", "") == 0);            /* padrao vazio */
    assert(kmp_buscar("", "") == 0);
    assert(kmp_buscar("aaaab", "aaab") == 1);      /* exige retrocesso via tabela */
    assert(kmp_buscar("ababababc", "abababc") == 2);
    assert(kmp_buscar("x", "x") == 0);
    assert(kmp_contar("aaaa", "aa") == 3);         /* sobrepostas */
    assert(kmp_contar("abracadabra", "abra") == 2);
    assert(kmp_contar("abc", "d") == 0);
    assert(kmp_contar("abc", "") == 0);
    assert(kmp_contar("", "a") == 0);
    assert(kmp_contar("abababa", "aba") == 3);
    puts("kmp ok");
    return 0;
}
