#include "bignum.h"
#include <stdlib.h>
#include <string.h>

static int valida(const char *s) {
    if (!s || !*s) return 0;
    for (; *s; s++) if (*s < '0' || *s > '9') return 0;
    return 1;
}

/* Remove zeros a esquerda (deixa pelo menos um digito) deslocando o buffer. */
static char *normalizar(char *s) {
    size_t i = 0, n = strlen(s);
    while (i + 1 < n && s[i] == '0') i++;
    if (i) memmove(s, s + i, n - i + 1);
    return s;
}

char *big_soma(const char *a, const char *b) {
    if (!valida(a) || !valida(b)) return NULL;
    size_t la = strlen(a), lb = strlen(b);
    size_t max = la > lb ? la : lb;
    char *r = malloc(max + 2);
    if (!r) return NULL;
    r[max + 1] = '\0';
    int carry = 0;
    for (size_t k = 0; k < max; k++) {
        int da = k < la ? a[la - 1 - k] - '0' : 0;
        int db = k < lb ? b[lb - 1 - k] - '0' : 0;
        int s = da + db + carry;
        r[max - k] = (char)('0' + s % 10);
        carry = s / 10;
    }
    r[0] = (char)('0' + carry);
    return normalizar(r);
}

char *big_mul(const char *a, const char *b) {
    if (!valida(a) || !valida(b)) return NULL;
    size_t la = strlen(a), lb = strlen(b), n = la + lb;
    unsigned *acc = calloc(n, sizeof *acc);   /* acc[0] = menos significativo */
    char *r = malloc(n + 1);
    if (!acc || !r) { free(acc); free(r); return NULL; }
    for (size_t i = 0; i < la; i++) {
        unsigned carry = 0;
        unsigned da = (unsigned)(a[la - 1 - i] - '0');
        for (size_t j = 0; j < lb; j++) {
            unsigned cur = acc[i + j] + da * (unsigned)(b[lb - 1 - j] - '0') + carry;
            acc[i + j] = cur % 10;
            carry = cur / 10;
        }
        acc[i + lb] += carry;     /* posicao ainda intocada nesta linha */
    }
    for (size_t k = 0; k < n; k++) r[n - 1 - k] = (char)('0' + acc[k]);
    r[n] = '\0';
    free(acc);
    return normalizar(r);
}

char *big_fatorial(unsigned n) {
    char *r = malloc(2);
    if (!r) return NULL;
    strcpy(r, "1");
    for (unsigned i = 2; i <= n; i++) {
        char buf[16];
        /* i cabe em 10 digitos; converte sem snprintf para ficar simples */
        size_t p = sizeof buf - 1;
        buf[p] = '\0';
        for (unsigned x = i; x > 0; x /= 10) buf[--p] = (char)('0' + x % 10);
        char *novo = big_mul(r, buf + p);
        free(r);
        if (!novo) return NULL;
        r = novo;
    }
    return r;
}
