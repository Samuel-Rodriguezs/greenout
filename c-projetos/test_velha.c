#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "velha.h"

int main(void) {
    char t[10] = "XX OO    ";
    /* X vence jogando em 2 (mesmo com O prestes a vencer, X joga primeiro). */
    assert(velha_melhor_jogada(t, 'X') == 2);
    /* O precisa bloquear. */
    char b[10] = "XX  O    ";
    assert(velha_melhor_jogada(b, 'O') == 2);
    assert(velha_resultado("XXXOO    ") == 'X');
    assert(velha_resultado("XOXXOOOXX") == 'E');
    assert(velha_resultado("         ") == 0);
    assert(velha_melhor_jogada("XOXXOOOXX", 'X') == -1);

    /* Dois jogadores perfeitos sempre empatam. */
    char j[10];
    memset(j, ' ', 9); j[9] = 0;
    char vez = 'X';
    while (!velha_resultado(j)) {
        int m = velha_melhor_jogada(j, vez);
        assert(m >= 0 && j[m] == ' ');
        j[m] = vez;
        vez = vez == 'X' ? 'O' : 'X';
    }
    assert(velha_resultado(j) == 'E');
    puts("velha ok");
    return 0;
}
