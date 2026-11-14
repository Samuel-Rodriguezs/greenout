#include "pilha_chamadas.h"

#include <stdio.h>
#include <stdlib.h>

#define CAB 2 /* palavras de cabecalho por frame */

struct PilhaChamadas {
    int64_t *mem;
    size_t cap;
    size_t sp;           /* proxima palavra livre */
    int64_t bp;          /* base do frame atual; -1 se nenhum */
    const char **nomes;  /* nomes[d] = funcao do frame de profundidade d */
    size_t prof;
};

PilhaChamadas *pc_criar(size_t palavras) {
    if (palavras < CAB) return NULL;
    PilhaChamadas *p = calloc(1, sizeof *p);
    if (!p) return NULL;
    p->mem = calloc(palavras, sizeof(int64_t));
    p->nomes = calloc(palavras / CAB, sizeof(char *)); /* no max cap/2 frames */
    if (!p->mem || !p->nomes) {
        pc_destruir(p);
        return NULL;
    }
    p->cap = palavras;
    p->bp = -1;
    return p;
}

void pc_destruir(PilhaChamadas *p) {
    if (!p) return;
    free(p->mem);
    free(p->nomes);
    free(p);
}

int pc_chamar(PilhaChamadas *p, const char *nome, int64_t retorno, size_t nlocais) {
    if (nlocais > p->cap || p->sp + CAB + nlocais > p->cap) return -1; /* estouro */
    size_t base = p->sp;
    p->mem[base] = retorno;
    p->mem[base + 1] = p->bp;
    for (size_t i = 0; i < nlocais; i++) p->mem[base + CAB + i] = 0;
    p->nomes[p->prof++] = nome;
    p->bp = (int64_t)base;
    p->sp = base + CAB + nlocais;
    return 0;
}

int pc_retornar(PilhaChamadas *p, int64_t *retorno) {
    if (p->bp < 0) return -1;
    size_t base = (size_t)p->bp;
    if (retorno) *retorno = p->mem[base];
    p->bp = p->mem[base + 1]; /* restaura o frame do chamador */
    p->sp = base;
    p->prof--;
    return 0;
}

/* numero de locais do frame atual */
static size_t nlocais_atual(const PilhaChamadas *p) {
    return p->sp - (size_t)p->bp - CAB;
}

int pc_local_set(PilhaChamadas *p, size_t i, int64_t valor) {
    if (p->bp < 0 || i >= nlocais_atual(p)) return -1;
    p->mem[(size_t)p->bp + CAB + i] = valor;
    return 0;
}

int pc_local_get(const PilhaChamadas *p, size_t i, int64_t *valor) {
    if (p->bp < 0 || i >= nlocais_atual(p)) return -1;
    *valor = p->mem[(size_t)p->bp + CAB + i];
    return 0;
}

size_t pc_profundidade(const PilhaChamadas *p) { return p->prof; }
size_t pc_palavras_usadas(const PilhaChamadas *p) { return p->sp; }

size_t pc_backtrace(const PilhaChamadas *p, char *buf, size_t cap) {
    size_t total = 0;
    int64_t bp = p->bp;
    size_t nivel = 0;
    while (bp >= 0) { /* segue a cadeia de frame pointers salvos */
        size_t d = p->prof - 1 - nivel;
        size_t restante = total < cap ? cap - total : 0;
        int w = snprintf(buf ? buf + (total < cap ? total : 0) : NULL, restante,
                         "#%zu %s ret=%lld\n", nivel, p->nomes[d],
                         (long long)p->mem[(size_t)bp]);
        total += (size_t)w;
        bp = p->mem[(size_t)bp + 1];
        nivel++;
    }
    if (cap > 0 && total == 0) buf[0] = '\0';
    return total;
}
