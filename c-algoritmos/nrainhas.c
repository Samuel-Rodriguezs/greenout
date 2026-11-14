#include "nrainhas.h"

#define N_MAX 16

/* colunas, diagonais "\" e "/" ocupadas como mascaras; a cada linha
 * deslocamos as diagonais para acompanhar o tabuleiro. */
static long contar(unsigned todas, unsigned cols, unsigned d1, unsigned d2) {
    if (cols == todas) return 1;
    long total = 0;
    unsigned livres = todas & ~(cols | d1 | d2);
    while (livres) {
        unsigned bit = livres & (0u - livres);
        livres ^= bit;
        total += contar(todas, cols | bit, ((d1 | bit) << 1) & todas, (d2 | bit) >> 1);
    }
    return total;
}

static int achar(int n, int linha, unsigned todas, unsigned cols, unsigned d1,
                 unsigned d2, int *col) {
    if (linha == n) return 1;
    unsigned livres = todas & ~(cols | d1 | d2);
    while (livres) {
        unsigned bit = livres & (0u - livres);       /* menor coluna primeiro */
        livres ^= bit;
        int c = 0;
        while (!((bit >> c) & 1u)) c++;
        col[linha] = c;
        if (achar(n, linha + 1, todas, cols | bit, ((d1 | bit) << 1) & todas,
                  (d2 | bit) >> 1, col))
            return 1;
    }
    return 0;
}

long nrainhas_contar(int n) {
    if (n < 0 || n > N_MAX) return -1;
    if (n == 0) return 1;
    return contar((1u << n) - 1u, 0, 0, 0);
}

int nrainhas_primeira(int n, int *col) {
    if (n < 0 || n > N_MAX) return -1;
    if (n == 0) return 1;
    return achar(n, 0, (1u << n) - 1u, 0, 0, 0, col);
}
