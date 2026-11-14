#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "strlib.h"

int main(void) {
    char *t = str_trim("  \t ola mundo \n");
    assert(strcmp(t, "ola mundo") == 0);
    free(t);
    t = str_trim("   ");
    assert(strcmp(t, "") == 0);
    free(t);

    size_t n;
    char **v = str_split("a,b,,c", ",", &n);
    assert(n == 4 && !strcmp(v[0], "a") && !strcmp(v[2], "") && !strcmp(v[3], "c"));
    char *j = str_join(v, n, " | ");
    assert(strcmp(j, "a | b |  | c") == 0);
    free(j);
    str_free_lista(v, n);

    v = str_split("sem separador", "::", &n);
    assert(n == 1 && strcmp(v[0], "sem separador") == 0);
    str_free_lista(v, n);
    assert(str_split("x", "", &n) == NULL);

    j = str_join(NULL, 0, ",");
    assert(strcmp(j, "") == 0);
    free(j);

    char *r = str_replace("o gato e o rato", "o", "00");
    assert(strcmp(r, "00 gat00 e 00 rat00") == 0);
    free(r);
    r = str_replace("aaa", "aa", "b");
    assert(strcmp(r, "ba") == 0);
    free(r);
    r = str_replace("abc", "x", "yy");
    assert(strcmp(r, "abc") == 0);
    free(r);
    r = str_replace("abc", "b", "");
    assert(strcmp(r, "ac") == 0);
    free(r);
    puts("strlib ok");
    return 0;
}
