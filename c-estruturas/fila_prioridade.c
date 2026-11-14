#include "fila_prioridade.h"
#include <stdlib.h>

Pq *pq_nova(void) {
    Pq *q = malloc(sizeof *q);
    if (!q) return NULL;
    q->itens = NULL;
    q->tam = q->cap = 0;
    q->prox_seq = 0;
    return q;
}

void pq_liberar(Pq *q) {
    if (!q) return;
    free(q->itens);
    free(q);
}

size_t pq_tam(const Pq *q) { return q->tam; }

/* a "vem antes" de b: maior prioridade, ou mesma prioridade e chegou antes. */
static bool antes(const ItemPq *a, const ItemPq *b) {
    if (a->prioridade != b->prioridade) return a->prioridade > b->prioridade;
    return a->seq < b->seq;
}

static void trocar(ItemPq *a, ItemPq *b) {
    ItemPq t = *a;
    *a = *b;
    *b = t;
}

bool pq_inserir(Pq *q, int valor, int prioridade) {
    if (q->tam == q->cap) {
        size_t nova = q->cap ? q->cap * 2 : 8;
        ItemPq *p = realloc(q->itens, nova * sizeof *p);
        if (!p) return false;
        q->itens = p;
        q->cap = nova;
    }
    size_t i = q->tam++;
    q->itens[i] = (ItemPq){valor, prioridade, q->prox_seq++};
    while (i > 0) {
        size_t pai = (i - 1) / 2;
        if (!antes(&q->itens[i], &q->itens[pai])) break;
        trocar(&q->itens[i], &q->itens[pai]);
        i = pai;
    }
    return true;
}

bool pq_espiar(const Pq *q, int *valor, int *prioridade) {
    if (q->tam == 0) return false;
    if (valor) *valor = q->itens[0].valor;
    if (prioridade) *prioridade = q->itens[0].prioridade;
    return true;
}

bool pq_remover(Pq *q, int *valor, int *prioridade) {
    if (!pq_espiar(q, valor, prioridade)) return false;
    q->itens[0] = q->itens[--q->tam];
    size_t i = 0;
    for (;;) {
        size_t e = 2 * i + 1, d = e + 1, m = i;
        if (e < q->tam && antes(&q->itens[e], &q->itens[m])) m = e;
        if (d < q->tam && antes(&q->itens[d], &q->itens[m])) m = d;
        if (m == i) break;
        trocar(&q->itens[i], &q->itens[m]);
        i = m;
    }
    return true;
}
