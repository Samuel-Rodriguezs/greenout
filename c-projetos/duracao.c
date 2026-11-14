#include "duracao.h"
#include <ctype.h>
#include <stdio.h>

int duracao_formatar(long long s, char *buf, size_t tam) {
    if (s < 0) s = 0;
    long long d = s / 86400, h = s % 86400 / 3600, m = s % 3600 / 60, seg = s % 60;
    if (s == 0) return snprintf(buf, tam, "0s");
    int n = 0;
    const char un[4] = {'d', 'h', 'm', 's'};
    long long v[4] = {d, h, m, seg};
    for (int i = 0; i < 4; i++) {
        if (!v[i]) continue;
        size_t resta = (size_t)n < tam ? tam - (size_t)n : 0;
        char *p = resta ? buf + n : NULL;
        n += snprintf(p, resta, "%s%lld%c", n ? " " : "", v[i], un[i]);
    }
    return n;
}

int duracao_relogio(long long s, char *buf, size_t tam) {
    if (s < 0) s = 0;
    return snprintf(buf, tam, "%02lld:%02lld:%02lld", s / 3600, s % 3600 / 60, s % 60);
}

int duracao_parse(const char *t, long long *out) {
    long long total = 0;
    int visto[4] = {0, 0, 0, 0}; /* cada unidade no maximo uma vez */
    if (!*t) return -1;
    while (*t) {
        if (!isdigit((unsigned char)*t)) return -1;
        long long n = 0;
        while (isdigit((unsigned char)*t)) {
            n = n * 10 + (*t++ - '0');
            if (n > 1000000000000LL) return -1;
        }
        long long mult;
        int idx;
        switch (*t++) {
        case 'd': mult = 86400; idx = 0; break;
        case 'h': mult = 3600; idx = 1; break;
        case 'm': mult = 60; idx = 2; break;
        case 's': mult = 1; idx = 3; break;
        default: return -1;
        }
        if (visto[idx]++) return -1;
        total += n * mult;
    }
    *out = total;
    return 0;
}

int duracao_hora12(long long s, char *buf, size_t tam) {
    s = ((s % 86400) + 86400) % 86400;
    long long h = s / 3600, m = s % 3600 / 60;
    const char *sufixo = h >= 12 ? "PM" : "AM";
    h %= 12;
    if (h == 0) h = 12;
    return snprintf(buf, tam, "%02lld:%02lld %s", h, m, sufixo);
}
