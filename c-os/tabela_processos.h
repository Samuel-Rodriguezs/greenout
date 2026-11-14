#ifndef TABELA_PROCESSOS_H
#define TABELA_PROCESSOS_H

#include <stddef.h>

/* Tabela de processos (PCBs) com o diagrama de estados classico:
 *
 *   NOVO -> PRONTO -> EXECUTANDO -> TERMINADO
 *             ^  ^        |  |
 *             |  +--------+  |   (preempcao)
 *             +-- BLOQUEADO <+   (espera de E/S)
 *
 * Apenas um processo pode estar EXECUTANDO por vez (uma CPU). */

typedef enum {
    PROC_NOVO,
    PROC_PRONTO,
    PROC_EXECUTANDO,
    PROC_BLOQUEADO,
    PROC_TERMINADO,
    PROC_NUM_ESTADOS
} ProcEstado;

enum {
    TP_OK = 0,
    TP_ERR_PID = -1,        /* pid inexistente */
    TP_ERR_TRANSICAO = -2,  /* transicao invalida a partir do estado atual */
    TP_ERR_CPU_OCUPADA = -3 /* ja existe um processo executando */
};

typedef struct TabelaProc TabelaProc;

TabelaProc *tp_criar(size_t capacidade);
void tp_destruir(TabelaProc *t);

/* Cria um processo no estado NOVO. Retorna o pid (>= 1, nunca reutilizado)
 * ou -1 se a tabela estiver cheia ou o pai nao existir (ppid 0 = sem pai). */
int tp_criar_proc(TabelaProc *t, int ppid);

int tp_admitir(TabelaProc *t, int pid);      /* NOVO -> PRONTO */
int tp_despachar(TabelaProc *t, int pid);    /* PRONTO -> EXECUTANDO */
int tp_preemptar(TabelaProc *t, int pid);    /* EXECUTANDO -> PRONTO */
int tp_bloquear(TabelaProc *t, int pid);     /* EXECUTANDO -> BLOQUEADO */
int tp_desbloquear(TabelaProc *t, int pid);  /* BLOQUEADO -> PRONTO */
int tp_terminar(TabelaProc *t, int pid, int codigo); /* EXECUTANDO -> TERMINADO */
/* Mata de qualquer estado nao terminado (codigo de saida -9). */
int tp_matar(TabelaProc *t, int pid);
/* Colhe um processo TERMINADO (como wait): grava o codigo e libera a vaga. */
int tp_coletar(TabelaProc *t, int pid, int *codigo);

/* Estado do processo, ou -1 se o pid nao existe. */
int tp_estado(const TabelaProc *t, int pid);
int tp_ppid(const TabelaProc *t, int pid);
int tp_em_execucao(const TabelaProc *t); /* pid ou -1 */
size_t tp_contar(const TabelaProc *t, ProcEstado e);
size_t tp_total(const TabelaProc *t);
const char *tp_nome_estado(ProcEstado e);

#endif
