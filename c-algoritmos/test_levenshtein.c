#include <assert.h>
#include <stdio.h>
#include "levenshtein.h"

int main(void) {
    assert(levenshtein("", "") == 0);
    assert(levenshtein("", "abc") == 3);
    assert(levenshtein("abc", "") == 3);
    assert(levenshtein("abc", "abc") == 0);
    assert(levenshtein("kitten", "sitting") == 3);
    assert(levenshtein("sitting", "kitten") == 3);     /* simetria */
    assert(levenshtein("flaw", "lawn") == 2);
    assert(levenshtein("saturday", "sunday") == 3);
    assert(levenshtein("a", "b") == 1);
    assert(levenshtein("abc", "cba") == 2);
    assert(levenshtein("intention", "execution") == 5);
    assert(levenshtein("aaaa", "a") == 3);
    puts("levenshtein ok");
    return 0;
}
