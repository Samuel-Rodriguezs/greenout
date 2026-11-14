#include "paginacao.h"

#include <stdlib.h>

#define N_ENTRADAS 1024u
#define VPN_MAX 0xFFFFFu

typedef struct {
    uint32_t quadro;
    unsigned presente : 1;
    unsigned escrita : 1;
    unsigned acessado : 1;
    unsigned sujo : 1;
} Pte;

typedef struct {
    Pte e[N_ENTRADAS];
    unsigned usadas; /* entradas presentes */
} Tabela;

struct Paginacao {
    Tabela *dir[N_ENTRADAS];
    unsigned tabelas;
};

Paginacao *pag_criar(void) { return calloc(1, sizeof(Paginacao)); }

void pag_destruir(Paginacao *p) {
    if (!p) return;
    for (unsigned i = 0; i < N_ENTRADAS; i++) free(p->dir[i]);
    free(p);
}

int pag_mapear(Paginacao *p, uint32_t vpn, uint32_t quadro, int escrita) {
    if (vpn > VPN_MAX || quadro > VPN_MAX) return -1;
    unsigned d = vpn >> 10, t = vpn & 0x3FF;
    if (!p->dir[d]) {
        p->dir[d] = calloc(1, sizeof(Tabela));
        if (!p->dir[d]) return -1;
        p->tabelas++;
    }
    Pte *e = &p->dir[d]->e[t];
    if (!e->presente) p->dir[d]->usadas++;
    *e = (Pte){.quadro = quadro, .presente = 1, .escrita = escrita ? 1 : 0};
    return 0;
}

int pag_desmapear(Paginacao *p, uint32_t vpn) {
    if (vpn > VPN_MAX) return -1;
    unsigned d = vpn >> 10, t = vpn & 0x3FF;
    Tabela *tb = p->dir[d];
    if (!tb || !tb->e[t].presente) return -1;
    tb->e[t].presente = 0;
    if (--tb->usadas == 0) {
        free(tb);
        p->dir[d] = NULL;
        p->tabelas--;
    }
    return 0;
}

PagStatus pag_traduzir(Paginacao *p, uint32_t virt, int escrita, uint32_t *fisico) {
    uint32_t vpn = virt >> 12;
    Tabela *tb = p->dir[vpn >> 10];
    if (!tb || !tb->e[vpn & 0x3FF].presente) return PAG_FALTA;
    Pte *e = &tb->e[vpn & 0x3FF];
    if (escrita && !e->escrita) return PAG_PROTECAO;
    e->acessado = 1;
    if (escrita) e->sujo = 1;
    *fisico = (e->quadro << 12) | (virt & (PAG_TAM_PAGINA - 1));
    return PAG_OK;
}

static const Pte *buscar(const Paginacao *p, uint32_t vpn) {
    if (vpn > VPN_MAX) return NULL;
    const Tabela *tb = p->dir[vpn >> 10];
    if (!tb || !tb->e[vpn & 0x3FF].presente) return NULL;
    return &tb->e[vpn & 0x3FF];
}

int pag_sujo(const Paginacao *p, uint32_t vpn) {
    const Pte *e = buscar(p, vpn);
    return e ? e->sujo : 0;
}

int pag_acessado(const Paginacao *p, uint32_t vpn) {
    const Pte *e = buscar(p, vpn);
    return e ? e->acessado : 0;
}

unsigned pag_tabelas_alocadas(const Paginacao *p) { return p->tabelas; }
