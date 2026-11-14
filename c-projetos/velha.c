#include "velha.h"
#include <string.h>

static const int LINHAS[8][3] = {
    {0, 1, 2}, {3, 4, 5}, {6, 7, 8}, {0, 3, 6},
    {1, 4, 7}, {2, 5, 8}, {0, 4, 8}, {2, 4, 6}};

char velha_resultado(const char t[9]) {
    for (int i = 0; i < 8; i++) {
        char a = t[LINHAS[i][0]];
        if (a != VELHA_VAZIO && a == t[LINHAS[i][1]] && a == t[LINHAS[i][2]])
            return a;
    }
    for (int i = 0; i < 9; i++)
        if (t[i] == VELHA_VAZIO) return 0;
    return 'E';
}

static char outro(char j) { return j == 'X' ? 'O' : 'X'; }

/* Minimax: pontuacao do ponto de vista de 'eu' (+1 vitoria, -1 derrota).
 * Prefere vitorias rapidas e derrotas tardias usando a profundidade. */
static int minimax(char t[9], char vez, char eu, int prof) {
    char r = velha_resultado(t);
    if (r == eu) return 10 - prof;
    if (r == 'E') return 0;
    if (r) return prof - 10;
    int melhor = vez == eu ? -100 : 100;
    for (int i = 0; i < 9; i++) {
        if (t[i] != VELHA_VAZIO) continue;
        t[i] = vez;
        int s = minimax(t, outro(vez), eu, prof + 1);
        t[i] = VELHA_VAZIO;
        if (vez == eu ? s > melhor : s < melhor) melhor = s;
    }
    return melhor;
}

int velha_melhor_jogada(const char t[9], char jogador) {
    char c[9];
    memcpy(c, t, 9);
    int melhor = -1, pontos = -100;
    for (int i = 0; i < 9; i++) {
        if (c[i] != VELHA_VAZIO) continue;
        c[i] = jogador;
        int s = minimax(c, outro(jogador), jogador, 1);
        c[i] = VELHA_VAZIO;
        if (s > pontos) { pontos = s; melhor = i; }
    }
    return melhor;
}
