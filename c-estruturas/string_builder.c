#include "string_builder.h"
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

StringBuilder *sb_novo(void) {
    StringBuilder *sb = malloc(sizeof *sb);
    if (!sb) return NULL;
    sb->cap = 16;
    sb->dados = malloc(sb->cap);
    if (!sb->dados) {
        free(sb);
        return NULL;
    }
    sb->dados[0] = '\0';
    sb->tam = 0;
    return sb;
}

void sb_liberar(StringBuilder *sb) {
    if (!sb) return;
    free(sb->dados);
    free(sb);
}

size_t sb_tam(const StringBuilder *sb) { return sb->tam; }
const char *sb_str(const StringBuilder *sb) { return sb->dados; }

/* Garante espaco para mais 'extra' caracteres alem do '\0'. */
static bool reservar(StringBuilder *sb, size_t extra) {
    size_t precisa = sb->tam + extra + 1;
    if (precisa <= sb->cap) return true;
    size_t nova = sb->cap;
    while (nova < precisa) nova *= 2;
    char *p = realloc(sb->dados, nova);
    if (!p) return false;
    sb->dados = p;
    sb->cap = nova;
    return true;
}

bool sb_anexar_n(StringBuilder *sb, const char *s, size_t n) {
    if (!reservar(sb, n)) return false;
    memcpy(sb->dados + sb->tam, s, n);
    sb->tam += n;
    sb->dados[sb->tam] = '\0';
    return true;
}

bool sb_anexar(StringBuilder *sb, const char *s) { return sb_anexar_n(sb, s, strlen(s)); }
bool sb_anexar_char(StringBuilder *sb, char c) { return sb_anexar_n(sb, &c, 1); }

bool sb_anexar_fmt(StringBuilder *sb, const char *fmt, ...) {
    va_list ap, copia;
    va_start(ap, fmt);
    va_copy(copia, ap);
    int n = vsnprintf(NULL, 0, fmt, ap);   /* primeiro mede */
    va_end(ap);
    bool ok = false;
    if (n >= 0 && reservar(sb, (size_t)n)) {
        vsnprintf(sb->dados + sb->tam, (size_t)n + 1, fmt, copia);
        sb->tam += (size_t)n;
        ok = true;
    }
    va_end(copia);
    return ok;
}

void sb_limpar(StringBuilder *sb) {
    sb->tam = 0;
    sb->dados[0] = '\0';
}

char *sb_destacar(StringBuilder *sb) {
    char *novo = malloc(16);
    if (!novo) return NULL;
    novo[0] = '\0';
    char *res = sb->dados;
    sb->dados = novo;
    sb->cap = 16;
    sb->tam = 0;
    return res;
}
