#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "lcs.h"

/* Confere que s e subsequencia de t. */
static int eh_subseq(const char *s, const char *t) {
    while (*s && *t) { if (*s == *t) s++; t++; }
    return *s == '\0';
}

int main(void) {
    assert(lcs_tamanho("", "") == 0);
    assert(lcs_tamanho("abc", "") == 0);
    assert(lcs_tamanho("", "abc") == 0);
    assert(lcs_tamanho("abc", "abc") == 3);
    assert(lcs_tamanho("abc", "def") == 0);
    assert(lcs_tamanho("AGGTAB", "GXTXAYB") == 4);
    assert(lcs_tamanho("ABCBDAB", "BDCABA") == 4);

    char *s = lcs_string("AGGTAB", "GXTXAYB");
    assert(s && strcmp(s, "GTAB") == 0);
    free(s);
    s = lcs_string("ABCBDAB", "BDCABA");
    assert(s && strlen(s) == 4 && eh_subseq(s, "ABCBDAB") && eh_subseq(s, "BDCABA"));
    free(s);
    s = lcs_string("", "xyz");
    assert(s && s[0] == '\0');
    free(s);
    s = lcs_string("aaa", "aa");
    assert(s && strcmp(s, "aa") == 0);
    free(s);
    puts("lcs ok");
    return 0;
}
