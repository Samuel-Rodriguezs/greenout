#include "args.h"
#include <string.h>

void args_init(Args *a, int argc, char **argv, const char *optstring) {
    a->argc = argc;
    a->argv = argv;
    a->optstring = optstring;
    a->indice = 1;
    a->pos = 0;
    a->optarg = NULL;
    a->optopt = 0;
}

int args_proximo(Args *a) {
    a->optarg = NULL;
    if (a->pos == 0) {
        if (a->indice >= a->argc) return -1;
        char *s = a->argv[a->indice];
        if (s[0] != '-' || s[1] == 0) return -1; /* nao-opcao (ou "-") */
        if (strcmp(s, "--") == 0) { a->indice++; return -1; }
        a->pos = 1;
    }
    char *s = a->argv[a->indice];
    char c = s[a->pos++];
    const char *d = strchr(a->optstring, c);
    int fim_grupo = s[a->pos] == 0;
    if (!d || c == ':') {
        a->optopt = c;
        if (fim_grupo) { a->indice++; a->pos = 0; }
        return '?';
    }
    if (d[1] == ':') { /* precisa de argumento */
        if (!fim_grupo) {
            a->optarg = s + a->pos;
            a->indice++;
        } else if (a->indice + 1 < a->argc) {
            a->optarg = a->argv[a->indice + 1];
            a->indice += 2;
        } else {
            a->optopt = c;
            a->indice++;
            a->pos = 0;
            return '?';
        }
        a->pos = 0;
    } else if (fim_grupo) {
        a->indice++;
        a->pos = 0;
    }
    return c;
}
