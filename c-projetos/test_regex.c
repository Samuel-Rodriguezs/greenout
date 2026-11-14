#include <assert.h>
#include <stdio.h>
#include "regex.h"

int main(void) {
    assert(regex_busca("abc", "xxabcxx"));
    assert(!regex_busca("abc", "ab"));
    assert(regex_busca("^abc", "abcd"));
    assert(!regex_busca("^abc", "xabc"));
    assert(regex_busca("abc$", "xxabc"));
    assert(!regex_busca("abc$", "abcx"));
    assert(regex_busca("^abc$", "abc"));
    assert(regex_busca("a.c", "abc"));
    assert(!regex_busca("a.c", "ac"));
    assert(regex_busca("ab*c", "ac"));
    assert(regex_busca("ab*c", "abbbc"));
    assert(regex_busca("^a.*z$", "a123z"));
    assert(regex_busca("^a.*z$", "az"));
    assert(!regex_busca("^a.*z$", "a123"));
    assert(regex_busca("", "qualquer"));
    assert(regex_busca("^$", ""));
    assert(!regex_busca("^$", "x"));
    assert(regex_busca("x*", ""));
    assert(regex_busca("a*a*a*b", "aaaaab"));
    puts("regex ok");
    return 0;
}
