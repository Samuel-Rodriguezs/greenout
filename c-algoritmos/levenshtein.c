#include "levenshtein.h"
#include <stdlib.h>
#include <string.h>

size_t levenshtein(const char *a, const char *b) {
    size_t la = strlen(a), lb = strlen(b);
    /* garante que b e a mais curta (linhas menores) */
    if (lb > la) {
        const char *t = a; a = b; b = t;
        size_t tl = la; la = lb; lb = tl;
    }
    if (lb == 0) return la;
    size_t *linha = malloc((lb + 1) * sizeof *linha);
    if (!linha) return (size_t)-1;
    for (size_t j = 0; j <= lb; j++) linha[j] = j;
    for (size_t i = 1; i <= la; i++) {
        size_t diag = linha[0];      /* valor de d[i-1][j-1] */
        linha[0] = i;
        for (size_t j = 1; j <= lb; j++) {
            size_t acima = linha[j];
            size_t custo = (a[i - 1] == b[j - 1]) ? 0 : 1;
            size_t v = diag + custo;
            if (acima + 1 < v) v = acima + 1;
            if (linha[j - 1] + 1 < v) v = linha[j - 1] + 1;
            linha[j] = v;
            diag = acima;
        }
    }
    size_t r = linha[lb];
    free(linha);
    return r;
}
