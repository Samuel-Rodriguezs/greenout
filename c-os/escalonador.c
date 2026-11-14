#include "escalonador.h"

#include <stdlib.h>

typedef enum { CRIT_FCFS, CRIT_SJF, CRIT_PRIO } Criterio;

static int validar(const Proc *p, size_t n) {
    for (size_t i = 0; i < n; i++)
        if (p[i].burst <= 0) return -1;
    return 0;
}

static void calcular_metricas(const Proc *p, size_t n, Resultado *res, Metricas *m) {
    for (size_t i = 0; i < n; i++) {
        res[i].pid = p[i].pid;
        res[i].retorno = res[i].termino - p[i].chegada;
        res[i].espera = res[i].retorno - p[i].burst;
    }
    if (!m) return;
    *m = (Metricas){0};
    if (n == 0) return;
    for (size_t i = 0; i < n; i++) {
        m->espera_media += res[i].espera;
        m->retorno_medio += res[i].retorno;
        m->resposta_media += res[i].resposta;
        if (res[i].termino > m->tempo_total) m->tempo_total = res[i].termino;
    }
    m->espera_media /= (double)n;
    m->retorno_medio /= (double)n;
    m->resposta_media /= (double)n;
}

/* a e "melhor" que b segundo o criterio? (desempate: chegada, depois indice) */
static int melhor(const Proc *p, size_t a, size_t b, Criterio c) {
    int ka = 0, kb = 0;
    if (c == CRIT_SJF) {
        ka = p[a].burst;
        kb = p[b].burst;
    } else if (c == CRIT_PRIO) {
        ka = p[a].prioridade;
        kb = p[b].prioridade;
    }
    if (ka != kb) return ka < kb;
    if (p[a].chegada != p[b].chegada) return p[a].chegada < p[b].chegada;
    return a < b;
}

static int nao_preemptivo(const Proc *p, size_t n, Resultado *res, Metricas *m, Criterio c) {
    if (validar(p, n) < 0) return -1;
    unsigned char *feito = calloc(n ? n : 1, 1);
    if (!feito) return -1;
    int t = 0;
    for (size_t cont = 0; cont < n; cont++) {
        long esc = -1;
        int proxima = 0; /* menor chegada entre os pendentes, para pular ociosidade */
        int tem_prox = 0;
        for (size_t i = 0; i < n; i++) {
            if (feito[i]) continue;
            if (!tem_prox || p[i].chegada < proxima) {
                proxima = p[i].chegada;
                tem_prox = 1;
            }
            if (p[i].chegada <= t && (esc < 0 || melhor(p, i, (size_t)esc, c))) esc = (long)i;
        }
        if (esc < 0) { /* CPU ociosa ate a proxima chegada */
            t = proxima;
            cont--;
            continue;
        }
        res[esc].resposta = t - p[esc].chegada;
        t += p[esc].burst;
        res[esc].termino = t;
        feito[esc] = 1;
    }
    free(feito);
    calcular_metricas(p, n, res, m);
    return 0;
}

int esc_fcfs(const Proc *p, size_t n, Resultado *r, Metricas *m) {
    return nao_preemptivo(p, n, r, m, CRIT_FCFS);
}
int esc_sjf(const Proc *p, size_t n, Resultado *r, Metricas *m) {
    return nao_preemptivo(p, n, r, m, CRIT_SJF);
}
int esc_prioridade(const Proc *p, size_t n, Resultado *r, Metricas *m) {
    return nao_preemptivo(p, n, r, m, CRIT_PRIO);
}

int esc_rr(const Proc *p, size_t n, int quantum, Resultado *res, Metricas *m) {
    if (quantum <= 0 || validar(p, n) < 0) return -1;
    if (n == 0) {
        if (m) *m = (Metricas){0};
        return 0;
    }
    size_t *ordem = malloc(n * sizeof *ordem); /* indices por chegada (estavel) */
    size_t *fila = malloc(n * sizeof *fila);   /* circular: no max n na fila */
    int *resta = malloc(n * sizeof *resta);
    if (!ordem || !fila || !resta) {
        free(ordem);
        free(fila);
        free(resta);
        return -1;
    }
    for (size_t i = 0; i < n; i++) {
        size_t j = i;
        while (j > 0 && p[ordem[j - 1]].chegada > p[i].chegada) {
            ordem[j] = ordem[j - 1];
            j--;
        }
        ordem[j] = i;
        resta[i] = p[i].burst;
        res[i].resposta = -1;
    }
    size_t ini = 0, tam = 0, prox = 0, feitos = 0;
    int t = 0;
#define ADMITIR()                                                        \
    while (prox < n && p[ordem[prox]].chegada <= t) {                    \
        fila[(ini + tam++) % n] = ordem[prox++];                         \
    }
    while (feitos < n) {
        ADMITIR();
        if (tam == 0) { /* ocioso: salta para a proxima chegada */
            t = p[ordem[prox]].chegada;
            continue;
        }
        size_t i = fila[ini];
        ini = (ini + 1) % n;
        tam--;
        if (res[i].resposta < 0) res[i].resposta = t - p[i].chegada;
        int fatia = resta[i] < quantum ? resta[i] : quantum;
        t += fatia;
        resta[i] -= fatia;
        ADMITIR();
        if (resta[i] > 0) {
            fila[(ini + tam++) % n] = i;
        } else {
            res[i].termino = t;
            feitos++;
        }
    }
#undef ADMITIR
    free(ordem);
    free(fila);
    free(resta);
    calcular_metricas(p, n, res, m);
    return 0;
}
