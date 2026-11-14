#include "relogio.h"

#include <stdlib.h>

typedef struct {
    int id;
    unsigned long vence;
    unsigned long periodo;
    RelTratador tratador;
    void *ctx;
    int ativo;
} Evento;

struct Relogio {
    Evento *ev;
    size_t n, cap;
    unsigned long agora;
    int proximo_id;
};

Relogio *rel_criar(void) {
    Relogio *r = calloc(1, sizeof *r);
    if (r) r->proximo_id = 1;
    return r;
}

void rel_destruir(Relogio *r) {
    if (!r) return;
    free(r->ev);
    free(r);
}

int rel_agendar(Relogio *r, unsigned long atraso, unsigned long periodo,
                RelTratador tratador, void *ctx) {
    if (atraso == 0 || !tratador) return -1;
    if (r->n == r->cap) {
        size_t nc = r->cap ? r->cap * 2 : 4;
        Evento *ne = realloc(r->ev, nc * sizeof *ne);
        if (!ne) return -1;
        r->ev = ne;
        r->cap = nc;
    }
    int id = r->proximo_id++;
    r->ev[r->n++] = (Evento){id, r->agora + atraso, periodo, tratador, ctx, 1};
    return id;
}

int rel_cancelar(Relogio *r, int id) {
    for (size_t i = 0; i < r->n; i++)
        if (r->ev[i].id == id && r->ev[i].ativo) {
            r->ev[i].ativo = 0;
            return 0;
        }
    return -1;
}

int rel_tick(Relogio *r) {
    r->agora++;
    int disparados = 0;
    /* indice (nao ponteiro): um tratador pode agendar e realocar o vetor */
    for (size_t i = 0; i < r->n; i++) {
        if (!r->ev[i].ativo || r->ev[i].vence != r->agora) continue;
        RelTratador t = r->ev[i].tratador;
        void *ctx = r->ev[i].ctx;
        int id = r->ev[i].id;
        if (r->ev[i].periodo) r->ev[i].vence += r->ev[i].periodo;
        else r->ev[i].ativo = 0;
        t(ctx, r->agora, id);
        disparados++;
    }
    size_t k = 0; /* compacta eventos inativos */
    for (size_t i = 0; i < r->n; i++)
        if (r->ev[i].ativo) r->ev[k++] = r->ev[i];
    r->n = k;
    return disparados;
}

int rel_avancar(Relogio *r, unsigned long ticks) {
    int total = 0;
    while (ticks--) total += rel_tick(r);
    return total;
}

unsigned long rel_agora(const Relogio *r) { return r->agora; }

size_t rel_pendentes(const Relogio *r) {
    size_t c = 0;
    for (size_t i = 0; i < r->n; i++) c += r->ev[i].ativo;
    return c;
}
