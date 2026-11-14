#include "tlb.h"

#include <stdlib.h>

typedef struct {
    uint32_t vpn;
    uint32_t quadro;
    unsigned long uso; /* relogio logico do ultimo acesso */
    int valida;
} Entrada;

struct Tlb {
    Entrada *e;
    size_t cap;
    unsigned long relogio;
    unsigned long acertos, faltas;
};

Tlb *tlb_criar(size_t capacidade) {
    if (capacidade == 0) return NULL;
    Tlb *t = calloc(1, sizeof *t);
    if (!t) return NULL;
    t->e = calloc(capacidade, sizeof(Entrada));
    if (!t->e) {
        free(t);
        return NULL;
    }
    t->cap = capacidade;
    return t;
}

void tlb_destruir(Tlb *t) {
    if (!t) return;
    free(t->e);
    free(t);
}

static Entrada *achar(Tlb *t, uint32_t vpn) {
    for (size_t i = 0; i < t->cap; i++)
        if (t->e[i].valida && t->e[i].vpn == vpn) return &t->e[i];
    return NULL;
}

int tlb_buscar(Tlb *t, uint32_t vpn, uint32_t *quadro) {
    Entrada *e = achar(t, vpn);
    if (!e) {
        t->faltas++;
        return 0;
    }
    e->uso = ++t->relogio;
    t->acertos++;
    *quadro = e->quadro;
    return 1;
}

void tlb_inserir(Tlb *t, uint32_t vpn, uint32_t quadro) {
    Entrada *alvo = achar(t, vpn);
    if (!alvo) {
        /* prefere uma entrada invalida; senao a de menor `uso` (LRU) */
        for (size_t i = 0; i < t->cap; i++) {
            Entrada *c = &t->e[i];
            if (!c->valida) {
                alvo = c;
                break;
            }
            if (!alvo || c->uso < alvo->uso) alvo = c;
        }
    }
    *alvo = (Entrada){vpn, quadro, ++t->relogio, 1};
}

int tlb_invalidar(Tlb *t, uint32_t vpn) {
    Entrada *e = achar(t, vpn);
    if (!e) return 0;
    e->valida = 0;
    return 1;
}

void tlb_limpar(Tlb *t) {
    for (size_t i = 0; i < t->cap; i++) t->e[i].valida = 0;
}

size_t tlb_tamanho(const Tlb *t) {
    size_t n = 0;
    for (size_t i = 0; i < t->cap; i++) n += t->e[i].valida;
    return n;
}

unsigned long tlb_acertos(const Tlb *t) { return t->acertos; }
unsigned long tlb_faltas(const Tlb *t) { return t->faltas; }
