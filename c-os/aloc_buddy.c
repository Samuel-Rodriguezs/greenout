#include "aloc_buddy.h"

#include <stdlib.h>

struct Buddy {
    size_t bloco_min;
    unsigned ordem_max;
    size_t unidades;      /* numero de blocos minimos = 2^ordem_max */
    size_t *livres;       /* livres[o*unidades + i]: offsets livres da ordem o */
    size_t *n_livres;     /* contagem por ordem */
    signed char *ordem_alocada; /* por bloco minimo: ordem do bloco alocado ou -1 */
};

#define LISTA(b, o) ((b)->livres + (size_t)(o) * (b)->unidades)

Buddy *buddy_criar(size_t bloco_min, unsigned ordem_max) {
    if (bloco_min == 0 || ordem_max > 30) return NULL;
    Buddy *b = calloc(1, sizeof *b);
    if (!b) return NULL;
    b->bloco_min = bloco_min;
    b->ordem_max = ordem_max;
    b->unidades = (size_t)1 << ordem_max;
    b->livres = calloc((ordem_max + 1) * b->unidades, sizeof(size_t));
    b->n_livres = calloc(ordem_max + 1, sizeof(size_t));
    b->ordem_alocada = malloc(b->unidades);
    if (!b->livres || !b->n_livres || !b->ordem_alocada) {
        buddy_destruir(b);
        return NULL;
    }
    for (size_t i = 0; i < b->unidades; i++) b->ordem_alocada[i] = -1;
    LISTA(b, ordem_max)[0] = 0;
    b->n_livres[ordem_max] = 1;
    return b;
}

void buddy_destruir(Buddy *b) {
    if (!b) return;
    free(b->livres);
    free(b->n_livres);
    free(b->ordem_alocada);
    free(b);
}

/* menor ordem cujo bloco comporta `tam`; -1 se nao couber */
static int ordem_para(const Buddy *b, size_t tam) {
    if (tam == 0) return -1;
    size_t tamanho = b->bloco_min;
    for (unsigned o = 0; o <= b->ordem_max; o++, tamanho <<= 1)
        if (tamanho >= tam) return (int)o;
    return -1;
}

size_t buddy_tamanho_reservado(const Buddy *b, size_t tam) {
    int o = ordem_para(b, tam);
    return o < 0 ? 0 : b->bloco_min << o;
}

long buddy_alocar(Buddy *b, size_t tam) {
    int o = ordem_para(b, tam);
    if (o < 0) return -1;
    unsigned k = (unsigned)o;
    while (k <= b->ordem_max && b->n_livres[k] == 0) k++;
    if (k > b->ordem_max) return -1;
    size_t un = LISTA(b, k)[--b->n_livres[k]]; /* offset em unidades */
    while (k > (unsigned)o) { /* divide, devolvendo a metade superior */
        k--;
        LISTA(b, k)[b->n_livres[k]++] = un + ((size_t)1 << k);
    }
    b->ordem_alocada[un] = (signed char)o;
    return (long)(un * b->bloco_min);
}

int buddy_liberar(Buddy *b, long endereco) {
    if (!b || endereco < 0 || (size_t)endereco % b->bloco_min) return -1;
    size_t un = (size_t)endereco / b->bloco_min;
    if (un >= b->unidades || b->ordem_alocada[un] < 0) return -1;
    unsigned o = (unsigned)b->ordem_alocada[un];
    b->ordem_alocada[un] = -1;
    while (o < b->ordem_max) { /* funde com o buddy enquanto ele estiver livre */
        size_t amigo = un ^ ((size_t)1 << o);
        size_t *l = LISTA(b, o);
        size_t i = 0;
        while (i < b->n_livres[o] && l[i] != amigo) i++;
        if (i == b->n_livres[o]) break;
        l[i] = l[--b->n_livres[o]];
        if (amigo < un) un = amigo;
        o++;
    }
    LISTA(b, o)[b->n_livres[o]++] = un;
    return 0;
}

size_t buddy_livre_total(const Buddy *b) {
    size_t s = 0;
    for (unsigned o = 0; o <= b->ordem_max; o++)
        s += b->n_livres[o] * (b->bloco_min << o);
    return s;
}

size_t buddy_maior_livre(const Buddy *b) {
    for (unsigned o = b->ordem_max + 1; o-- > 0;)
        if (b->n_livres[o]) return b->bloco_min << o;
    return 0;
}

size_t buddy_livres_na_ordem(const Buddy *b, unsigned ordem) {
    return ordem > b->ordem_max ? 0 : b->n_livres[ordem];
}
