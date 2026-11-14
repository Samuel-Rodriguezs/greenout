#include "strlib.h"
#include <ctype.h>
#include <stdlib.h>
#include <string.h>

/* Copia n bytes de s para uma string nova terminada em '\0'. */
static char *copia(const char *s, size_t n) {
    char *r = malloc(n + 1);
    if (!r) return NULL;
    memcpy(r, s, n);
    r[n] = 0;
    return r;
}

char *str_trim(const char *s) {
    while (isspace((unsigned char)*s)) s++;
    size_t n = strlen(s);
    while (n > 0 && isspace((unsigned char)s[n - 1])) n--;
    return copia(s, n);
}

void str_free_lista(char **v, size_t n) {
    if (!v) return;
    for (size_t i = 0; i < n; i++) free(v[i]);
    free(v);
}

char **str_split(const char *s, const char *sep, size_t *n) {
    size_t ls = strlen(sep), cnt = 1;
    if (ls == 0) return NULL;
    for (const char *p = s; (p = strstr(p, sep)); p += ls) cnt++;
    char **v = calloc(cnt, sizeof *v);
    if (!v) return NULL;
    size_t i = 0;
    const char *ini = s, *p;
    while ((p = strstr(ini, sep))) {
        if (!(v[i++] = copia(ini, (size_t)(p - ini)))) goto erro;
        ini = p + ls;
    }
    if (!(v[i++] = copia(ini, strlen(ini)))) goto erro;
    *n = cnt;
    return v;
erro:
    str_free_lista(v, cnt);
    return NULL;
}

char *str_join(char *const *v, size_t n, const char *sep) {
    size_t ls = strlen(sep), tot = 1;
    for (size_t i = 0; i < n; i++) tot += strlen(v[i]) + (i ? ls : 0);
    char *r = malloc(tot), *w = r;
    if (!r) return NULL;
    for (size_t i = 0; i < n; i++) {
        if (i) { memcpy(w, sep, ls); w += ls; }
        size_t l = strlen(v[i]);
        memcpy(w, v[i], l);
        w += l;
    }
    *w = 0;
    return r;
}

char *str_replace(const char *s, const char *de, const char *para) {
    size_t ld = strlen(de), lp = strlen(para), cnt = 0;
    if (ld == 0) return copia(s, strlen(s));
    for (const char *p = s; (p = strstr(p, de)); p += ld) cnt++;
    char *r = malloc(strlen(s) + cnt * lp - cnt * ld + 1), *w = r;
    if (!r) return NULL;
    const char *p;
    while ((p = strstr(s, de))) {
        memcpy(w, s, (size_t)(p - s)); w += p - s;
        memcpy(w, para, lp); w += lp;
        s = p + ld;
    }
    strcpy(w, s);
    return r;
}
