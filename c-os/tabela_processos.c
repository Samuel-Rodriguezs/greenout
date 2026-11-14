#include "tabela_processos.h"

#include <stdlib.h>

typedef struct {
    int pid;      /* 0 = vaga livre */
    int ppid;
    ProcEstado estado;
    int codigo;
} Pcb;

struct TabelaProc {
    Pcb *pcb;
    size_t cap;
    size_t total;
    int proximo_pid;
};

TabelaProc *tp_criar(size_t capacidade) {
    if (capacidade == 0) return NULL;
    TabelaProc *t = calloc(1, sizeof *t);
    if (!t) return NULL;
    t->pcb = calloc(capacidade, sizeof(Pcb));
    if (!t->pcb) {
        free(t);
        return NULL;
    }
    t->cap = capacidade;
    t->proximo_pid = 1;
    return t;
}

void tp_destruir(TabelaProc *t) {
    if (!t) return;
    free(t->pcb);
    free(t);
}

static Pcb *achar(const TabelaProc *t, int pid) {
    if (pid <= 0) return NULL;
    for (size_t i = 0; i < t->cap; i++)
        if (t->pcb[i].pid == pid) return &t->pcb[i];
    return NULL;
}

int tp_criar_proc(TabelaProc *t, int ppid) {
    if (ppid != 0 && !achar(t, ppid)) return -1;
    for (size_t i = 0; i < t->cap; i++) {
        if (t->pcb[i].pid != 0) continue;
        t->pcb[i] = (Pcb){t->proximo_pid++, ppid, PROC_NOVO, 0};
        t->total++;
        return t->pcb[i].pid;
    }
    return -1;
}

/* transicao generica: exige estado `de`, vai para `para` */
static int transitar(TabelaProc *t, int pid, ProcEstado de, ProcEstado para) {
    Pcb *p = achar(t, pid);
    if (!p) return TP_ERR_PID;
    if (p->estado != de) return TP_ERR_TRANSICAO;
    p->estado = para;
    return TP_OK;
}

int tp_admitir(TabelaProc *t, int pid) {
    return transitar(t, pid, PROC_NOVO, PROC_PRONTO);
}

int tp_despachar(TabelaProc *t, int pid) {
    Pcb *p = achar(t, pid);
    if (!p) return TP_ERR_PID;
    if (p->estado != PROC_PRONTO) return TP_ERR_TRANSICAO;
    if (tp_em_execucao(t) >= 0) return TP_ERR_CPU_OCUPADA;
    p->estado = PROC_EXECUTANDO;
    return TP_OK;
}

int tp_preemptar(TabelaProc *t, int pid) {
    return transitar(t, pid, PROC_EXECUTANDO, PROC_PRONTO);
}

int tp_bloquear(TabelaProc *t, int pid) {
    return transitar(t, pid, PROC_EXECUTANDO, PROC_BLOQUEADO);
}

int tp_desbloquear(TabelaProc *t, int pid) {
    return transitar(t, pid, PROC_BLOQUEADO, PROC_PRONTO);
}

int tp_terminar(TabelaProc *t, int pid, int codigo) {
    int r = transitar(t, pid, PROC_EXECUTANDO, PROC_TERMINADO);
    if (r == TP_OK) achar(t, pid)->codigo = codigo;
    return r;
}

int tp_matar(TabelaProc *t, int pid) {
    Pcb *p = achar(t, pid);
    if (!p) return TP_ERR_PID;
    if (p->estado == PROC_TERMINADO) return TP_ERR_TRANSICAO;
    p->estado = PROC_TERMINADO;
    p->codigo = -9;
    return TP_OK;
}

int tp_coletar(TabelaProc *t, int pid, int *codigo) {
    Pcb *p = achar(t, pid);
    if (!p) return TP_ERR_PID;
    if (p->estado != PROC_TERMINADO) return TP_ERR_TRANSICAO;
    if (codigo) *codigo = p->codigo;
    for (size_t i = 0; i < t->cap; i++) /* filhos viram orfaos (ppid 0) */
        if (t->pcb[i].pid && t->pcb[i].ppid == pid) t->pcb[i].ppid = 0;
    p->pid = 0;
    t->total--;
    return TP_OK;
}

int tp_estado(const TabelaProc *t, int pid) {
    const Pcb *p = achar(t, pid);
    return p ? (int)p->estado : -1;
}

int tp_ppid(const TabelaProc *t, int pid) {
    const Pcb *p = achar(t, pid);
    return p ? p->ppid : -1;
}

int tp_em_execucao(const TabelaProc *t) {
    for (size_t i = 0; i < t->cap; i++)
        if (t->pcb[i].pid && t->pcb[i].estado == PROC_EXECUTANDO) return t->pcb[i].pid;
    return -1;
}

size_t tp_contar(const TabelaProc *t, ProcEstado e) {
    size_t n = 0;
    for (size_t i = 0; i < t->cap; i++)
        if (t->pcb[i].pid && t->pcb[i].estado == e) n++;
    return n;
}

size_t tp_total(const TabelaProc *t) { return t->total; }

const char *tp_nome_estado(ProcEstado e) {
    static const char *nomes[PROC_NUM_ESTADOS] = {"novo", "pronto", "executando",
                                                  "bloqueado", "terminado"};
    return e < PROC_NUM_ESTADOS ? nomes[e] : "?";
}
