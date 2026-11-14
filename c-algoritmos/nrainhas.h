#ifndef NRAINHAS_H
#define NRAINHAS_H

/* Problema das N rainhas por backtracking com mascaras de bits.
 * Valido para 0 <= n <= 16; fora disso retornam -1. */

/* Numero de solucoes distintas (n = 0 tem 1 solucao: tabuleiro vazio). */
long nrainhas_contar(int n);

/* Primeira solucao em ordem lexicografica: col[linha] = coluna da rainha.
 * col deve ter espaco para n inteiros. Retorna 1 se achou, 0 se nao existe
 * (n = 2, 3), -1 se n invalido. */
int nrainhas_primeira(int n, int *col);

#endif
