#ifndef VELHA_H
#define VELHA_H

/* Jogo da velha 3x3. Tabuleiro: 9 chars ' ', 'X' ou 'O'. */
#define VELHA_VAZIO ' '

/* Retorna 'X' ou 'O' se houver vencedor, 'E' em empate, 0 se em andamento. */
char velha_resultado(const char t[9]);
/* Melhor jogada (0..8) para 'jogador' via minimax; -1 se nao ha jogada. */
int velha_melhor_jogada(const char t[9], char jogador);

#endif
