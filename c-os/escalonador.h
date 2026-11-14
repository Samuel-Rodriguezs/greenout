#ifndef ESCALONADOR_H
#define ESCALONADOR_H

#include <stddef.h>

/* Escalonadores de CPU simulados (tempo discreto, inteiros). */

typedef struct {
    int pid;
    int chegada;
    int burst;       /* tempo de CPU necessario, > 0 */
    int prioridade;  /* menor valor = maior prioridade */
} Proc;

typedef struct {
    int pid;
    int termino;
    int retorno;   /* termino - chegada */
    int espera;    /* retorno - burst */
    int resposta;  /* primeira execucao - chegada */
} Resultado;

typedef struct {
    double espera_media;
    double retorno_medio;
    double resposta_media;
    int tempo_total; /* instante em que o ultimo processo termina */
} Metricas;

/* Todas escrevem `n` resultados em `res`, na mesma ordem de `procs`, e as
 * metricas em `m` (pode ser NULL). Retornam 0, ou -1 se algum burst <= 0
 * (ou quantum <= 0 no Round Robin). Nao-preemptivas: FCFS, SJF e prioridade;
 * empates sao resolvidos por chegada e depois pela ordem do vetor. */
int esc_fcfs(const Proc *procs, size_t n, Resultado *res, Metricas *m);
int esc_sjf(const Proc *procs, size_t n, Resultado *res, Metricas *m);
int esc_prioridade(const Proc *procs, size_t n, Resultado *res, Metricas *m);
/* Round Robin: chegadas novas entram na fila antes do processo preemptado. */
int esc_rr(const Proc *procs, size_t n, int quantum, Resultado *res, Metricas *m);

#endif
