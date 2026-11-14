#include "aloc_firstfit.h"

#include <stdlib.h>

typedef struct Bloco {
    size_t ini;
    size_t tam;
    int livre;
    struct Bloco *prox;
} Bloco;

struct AlocFF {
    size_t capacidade;
    Bloco *cabeca;
};

AlocFF *ff_criar(size_t capacidade) {
    if (capacidade == 0) return NULL;
    AlocFF *a = malloc(sizeof *a);
    Bloco *b = malloc(sizeof *b);
    if (!a || !b) {
        free(a);
        free(b);
        return NULL;
    }
    *b = (Bloco){0, capacidade, 1, NULL};
    a->capacidade = capacidade;
    a->cabeca = b;
    return a;
}

void ff_destruir(AlocFF *a) {
    if (!a) return;
    Bloco *b = a->cabeca;
    while (b) {
        Bloco *p = b->prox;
        free(b);
        b = p;
    }
    free(a);
}

long ff_alocar(AlocFF *a, size_t tam) {
    if (!a || tam == 0) return -1;
    for (Bloco *b = a->cabeca; b; b = b->prox) {
        if (!b->livre || b->tam < tam) continue;
        if (b->tam > tam) { /* divide: sobra vira novo bloco livre */
            Bloco *resto = malloc(sizeof *resto);
            if (!resto) return -1;
            *resto = (Bloco){b->ini + tam, b->tam - tam, 1, b->prox};
            b->prox = resto;
            b->tam = tam;
        }
        b->livre = 0;
        return (long)b->ini;
    }
    return -1;
}

int ff_liberar(AlocFF *a, long endereco) {
    if (!a || endereco < 0) return -1;
    Bloco *ant = NULL;
    Bloco *b = a->cabeca;
    while (b && b->ini != (size_t)endereco) {
        ant = b;
        b = b->prox;
    }
    if (!b || b->livre) return -1;
    b->livre = 1;
    /* coalescencia com o vizinho seguinte */
    if (b->prox && b->prox->livre) {
        Bloco *n = b->prox;
        b->tam += n->tam;
        b->prox = n->prox;
        free(n);
    }
    /* coalescencia com o vizinho anterior */
    if (ant && ant->livre) {
        ant->tam += b->tam;
        ant->prox = b->prox;
        free(b);
    }
    return 0;
}

size_t ff_livre_total(const AlocFF *a) {
    size_t s = 0;
    for (const Bloco *b = a->cabeca; b; b = b->prox)
        if (b->livre) s += b->tam;
    return s;
}

size_t ff_maior_livre(const AlocFF *a) {
    size_t m = 0;
    for (const Bloco *b = a->cabeca; b; b = b->prox)
        if (b->livre && b->tam > m) m = b->tam;
    return m;
}

size_t ff_blocos_livres(const AlocFF *a) {
    size_t n = 0;
    for (const Bloco *b = a->cabeca; b; b = b->prox)
        if (b->livre) n++;
    return n;
}

size_t ff_blocos_total(const AlocFF *a) {
    size_t n = 0;
    for (const Bloco *b = a->cabeca; b; b = b->prox) n++;
    return n;
}
