#include <assert.h>
#include <stdio.h>

#include "relogio.h"

/* registro dos disparos: (id, instante) na ordem em que ocorreram */
typedef struct {
    int id[64];
    unsigned long t[64];
    int n;
} Log;

static void registra(void *ctx, unsigned long agora, int id) {
    Log *l = ctx;
    l->id[l->n] = id;
    l->t[l->n++] = agora;
}

typedef struct {
    Relogio *r;
    Log *log;
    int alvo; /* id a cancelar */
} Ctx;

static void cancela_outro(void *vc, unsigned long agora, int id) {
    Ctx *c = vc;
    registra(c->log, agora, id);
    rel_cancelar(c->r, c->alvo);
}

static void reagenda(void *vc, unsigned long agora, int id) {
    Ctx *c = vc;
    registra(c->log, agora, id);
    /* dispara varios agendamentos para forcar realocacao do vetor interno */
    for (int i = 0; i < 20; i++) rel_agendar(c->r, 2, 0, registra, c->log);
}

int main(void) {
    Relogio *r = rel_criar();
    Log log = {0};
    assert(r && rel_agora(r) == 0 && rel_pendentes(r) == 0);

    /* argumentos invalidos */
    assert(rel_agendar(r, 0, 0, registra, &log) == -1);
    assert(rel_agendar(r, 1, 0, NULL, &log) == -1);

    /* unico disparo em t=3 e periodico (desde t=2, a cada 2) */
    int a = rel_agendar(r, 3, 0, registra, &log);
    int b = rel_agendar(r, 2, 2, registra, &log);
    assert(a == 1 && b == 2 && rel_pendentes(r) == 2);
    assert(rel_tick(r) == 0);               /* t=1 */
    assert(rel_tick(r) == 1);               /* t=2: b */
    assert(rel_tick(r) == 1);               /* t=3: a */
    assert(rel_avancar(r, 3) == 2);         /* t=4 b, t=5 nada, t=6 b */
    assert(log.n == 4);
    assert(log.id[0] == b && log.t[0] == 2);
    assert(log.id[1] == a && log.t[1] == 3);
    assert(log.id[2] == b && log.t[2] == 4 && log.id[3] == b && log.t[3] == 6);
    assert(rel_pendentes(r) == 1);          /* so b resta */

    /* cancelar o periodico */
    assert(rel_cancelar(r, b) == 0 && rel_cancelar(r, b) == -1);
    assert(rel_avancar(r, 10) == 0 && rel_pendentes(r) == 0);
    assert(rel_agora(r) == 16);

    /* mesmo instante: ordem de agendamento */
    log.n = 0;
    int x = rel_agendar(r, 2, 0, registra, &log);
    int y = rel_agendar(r, 2, 0, registra, &log);
    int z = rel_agendar(r, 1, 0, registra, &log);
    assert(rel_avancar(r, 2) == 3);
    assert(log.id[0] == z && log.id[1] == x && log.id[2] == y);
    assert(log.t[0] == 17 && log.t[1] == 18);

    /* tratador cancela outro evento do mesmo instante (que vem depois) */
    log.n = 0;
    Ctx c = {r, &log, 0};
    int p = rel_agendar(r, 1, 0, cancela_outro, &c);
    int q = rel_agendar(r, 1, 0, registra, &log);
    c.alvo = q;
    assert(rel_tick(r) == 1 && log.n == 1 && log.id[0] == p);
    assert(rel_pendentes(r) == 0);

    /* tratador agenda eventos (realocando o vetor) dentro do tick */
    log.n = 0;
    Ctx d = {r, &log, 0};
    rel_agendar(r, 1, 0, reagenda, &d);
    assert(rel_tick(r) == 1);
    assert(rel_pendentes(r) == 20);
    assert(rel_tick(r) == 0);               /* atraso 2: ainda nao venceu */
    assert(rel_tick(r) == 20);
    assert(rel_pendentes(r) == 0 && log.n == 21);

    /* periodo 1 dispara em todo tick */
    log.n = 0;
    int w = rel_agendar(r, 1, 1, registra, &log);
    assert(rel_avancar(r, 5) == 5 && log.n == 5);
    rel_cancelar(r, w);
    assert(rel_avancar(r, 3) == 0);

    rel_destruir(r);
    rel_destruir(NULL);
    puts("test_relogio ok");
    return 0;
}
