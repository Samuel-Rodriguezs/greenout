#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include "tokenizer.h"

int main(void) {
    size_t n;
    Token *t = tokenizar("3 + 4.5*(2 - 1)", &n);
    assert(t && n == 9);
    assert(t[0].tipo == TOK_NUM && t[0].valor == 3);
    assert(t[1].tipo == TOK_OP && t[1].op == '+');
    assert(t[2].valor == 4.5);
    assert(t[4].tipo == TOK_LPAREN);
    assert(t[8].tipo == TOK_RPAREN);
    free(t);
    t = tokenizar("", &n);
    assert(t && n == 0);
    free(t);
    assert(tokenizar("2 $ 3", &n) == NULL);
    puts("tokenizer ok");
    return 0;
}
