#include "regex.h"

static int aqui(const char *re, const char *txt);

/* Casa c* seguido do resto do padrao, com retrocesso. */
static int estrela(int c, const char *re, const char *txt) {
    do {
        if (aqui(re, txt)) return 1;
    } while (*txt != '\0' && (*txt++ == c || c == '.'));
    return 0;
}

/* Casa o padrao exatamente a partir do inicio do texto. */
static int aqui(const char *re, const char *txt) {
    if (re[0] == '\0') return 1;
    if (re[1] == '*') return estrela(re[0], re + 2, txt);
    if (re[0] == '$' && re[1] == '\0') return *txt == '\0';
    if (*txt != '\0' && (re[0] == '.' || re[0] == *txt))
        return aqui(re + 1, txt + 1);
    return 0;
}

int regex_busca(const char *re, const char *txt) {
    if (re[0] == '^') return aqui(re + 1, txt);
    do {
        if (aqui(re, txt)) return 1;
    } while (*txt++ != '\0');
    return 0;
}
