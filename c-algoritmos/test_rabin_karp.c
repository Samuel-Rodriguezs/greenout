#include <assert.h>
#include <stdio.h>
#include "rabin_karp.h"

int main(void) {
    assert(rabin_karp_buscar("abracadabra", "abra") == 0);
    assert(rabin_karp_buscar("abracadabra", "cad") == 4);
    assert(rabin_karp_buscar("abracadabra", "ra") == 2);
    assert(rabin_karp_buscar("abracadabra", "xyz") == -1);
    assert(rabin_karp_buscar("abc", "abcd") == -1);
    assert(rabin_karp_buscar("", "a") == -1);
    assert(rabin_karp_buscar("abc", "") == 0);
    assert(rabin_karp_buscar("abc", "abc") == 0);   /* padrao == texto */
    assert(rabin_karp_buscar("abc", "c") == 2);     /* ultima posicao */
    assert(rabin_karp_buscar("aaaab", "aaab") == 1);
    assert(rabin_karp_contar("aaaa", "aa") == 3);
    assert(rabin_karp_contar("abracadabra", "abra") == 2);
    assert(rabin_karp_contar("abc", "z") == 0);
    assert(rabin_karp_contar("abc", "") == 0);
    assert(rabin_karp_contar("ab", "abc") == 0);
    assert(rabin_karp_contar("\xff\xfe\xff\xfe", "\xff\xfe") == 2); /* bytes altos */
    puts("rabin_karp ok");
    return 0;
}
