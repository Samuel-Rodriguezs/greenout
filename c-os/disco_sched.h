#ifndef DISCO_SCHED_H
#define DISCO_SCHED_H

#include <stddef.h>

/* Escalonamento de braco de disco. Os pedidos sao numeros de cilindro em
 * [0, max_cil]. Todas as funcoes retornam o movimento total do braco (em
 * cilindros) ou -1 se algum pedido/cabeca estiver fora do intervalo. Se
 * `ordem` nao for NULL, recebe os `n` pedidos na ordem em que sao atendidos.
 *
 * SCAN e C-SCAN seguem a versao de livro-texto: o braco sempre vai ate a
 * borda do disco; o SCAN so volta se houver pedidos do outro lado, e o
 * C-SCAN so salta para a outra borda se houver pedidos la (o salto de
 * retorno conta no movimento total). */

long disco_fcfs(int cabeca, const int *reqs, size_t n, int max_cil, int *ordem);
long disco_sstf(int cabeca, const int *reqs, size_t n, int max_cil, int *ordem);
/* sobe != 0: o braco anda inicialmente em direcao aos cilindros maiores. */
long disco_scan(int cabeca, const int *reqs, size_t n, int max_cil, int sobe, int *ordem);
long disco_cscan(int cabeca, const int *reqs, size_t n, int max_cil, int sobe, int *ordem);

#endif
