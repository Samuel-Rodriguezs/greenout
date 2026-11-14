#include "tokenizer.h"
#include <ctype.h>
#include <stdlib.h>
#include <string.h>

Token *tokenizar(const char *expr, size_t *n) {
    size_t cap = 8, qtd = 0;
    Token *v = malloc(cap * sizeof *v);
    if (!v) return NULL;
    const char *p = expr;
    while (*p) {
        if (isspace((unsigned char)*p)) { p++; continue; }
        if (qtd == cap) {
            cap *= 2;
            Token *novo = realloc(v, cap * sizeof *v);
            if (!novo) { free(v); return NULL; }
            v = novo;
        }
        Token t = {TOK_NUM, 0, 0};
        if (isdigit((unsigned char)*p) || *p == '.') {
            char *fim;
            t.valor = strtod(p, &fim);
            if (fim == p) { free(v); return NULL; }
            p = fim;
        } else if (strchr("+-*/^", *p)) {
            t.tipo = TOK_OP; t.op = *p++;
        } else if (*p == '(') { t.tipo = TOK_LPAREN; p++; }
        else if (*p == ')') { t.tipo = TOK_RPAREN; p++; }
        else { free(v); return NULL; }
        v[qtd++] = t;
    }
    *n = qtd;
    return v;
}
