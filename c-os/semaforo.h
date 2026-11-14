#ifndef SEMAFORO_H
#define SEMAFORO_H

#include <stddef.h>

/* Semaforo contador simulado (sem threads reais): quem chama informa o
 * identificador do "processo". Processos que nao conseguem decrementar ficam
 * na fila de espera (FIFO) e sao acordados por sem_signal. */

enum { SEM_BLOQUEOU = 0, SEM_ADQUIRIU = 1, SEM_ERRO = -1 };

typedef struct Semaforo Semaforo;

/* `maximo` limita o valor (1 = mutex/binario); 0 = sem limite.
 * `cap_fila` = maximo de processos esperando. NULL se valor > maximo. */
Semaforo *sem_criar(int valor, size_t cap_fila, int maximo);
void sem_destruir(Semaforo *s);

/* P(): SEM_ADQUIRIU se decrementou; SEM_BLOQUEOU se o processo entrou na
 * fila; SEM_ERRO se a fila esta cheia ou o processo ja esta esperando. */
int sem_wait(Semaforo *s, int pid);
/* P() sem bloquear: 1 se decrementou, 0 caso contrario. */
int sem_trywait(Semaforo *s);
/* V(): se ha processo esperando, passa o recurso direto ao primeiro e
 * devolve 1 gravando seu pid em *acordado (pode ser NULL); senao incrementa
 * e devolve 0. SEM_ERRO se o incremento passaria de `maximo`. */
int sem_signal(Semaforo *s, int *acordado);

int sem_valor(const Semaforo *s);
size_t sem_esperando(const Semaforo *s);

#endif
