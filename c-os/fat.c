#include "fat.h"

#include <stdlib.h>
#include <string.h>

#define LIVRE 0
#define FIM (-1)

typedef struct {
    char nome[FAT_NOME_MAX + 1];
    long inicio; /* primeiro cluster; 0 = nenhum */
    size_t tamanho;
    int usado;
} Entrada;

struct Fat {
    long *tab; /* indices 1..n */
    size_t n;
    size_t tam_cluster;
    size_t livres;
    Entrada *dir;
    size_t max_arq;
    size_t arquivos;
};

Fat *fat_criar(size_t nclusters, size_t tam_cluster, size_t max_arquivos) {
    if (nclusters == 0 || tam_cluster == 0 || max_arquivos == 0) return NULL;
    Fat *f = calloc(1, sizeof *f);
    if (!f) return NULL;
    f->tab = calloc(nclusters + 1, sizeof(long));
    f->dir = calloc(max_arquivos, sizeof(Entrada));
    if (!f->tab || !f->dir) {
        fat_destruir(f);
        return NULL;
    }
    f->n = nclusters;
    f->tam_cluster = tam_cluster;
    f->livres = nclusters;
    f->max_arq = max_arquivos;
    return f;
}

void fat_destruir(Fat *f) {
    if (!f) return;
    free(f->tab);
    free(f->dir);
    free(f);
}

static Entrada *achar(const Fat *f, const char *nome) {
    for (size_t i = 0; i < f->max_arq; i++)
        if (f->dir[i].usado && strcmp(f->dir[i].nome, nome) == 0) return &f->dir[i];
    return NULL;
}

static size_t clusters_para(const Fat *f, size_t bytes) {
    return (bytes + f->tam_cluster - 1) / f->tam_cluster;
}

/* Aloca `n` clusters livres (os de menor numero) e devolve o primeiro; se
 * `ultimo` != 0 liga o fim da cadeia existente ao novo trecho. Pre-condicao:
 * f->livres >= n e n > 0. */
static long alocar(Fat *f, size_t n, long ultimo) {
    long primeiro = 0, ant = ultimo;
    size_t feitos = 0;
    for (long k = 1; k <= (long)f->n && feitos < n; k++) {
        if (f->tab[k] != LIVRE) continue;
        f->tab[k] = FIM;
        if (ant > 0) f->tab[ant] = k;
        if (!primeiro) primeiro = k;
        ant = k;
        feitos++;
    }
    f->livres -= n;
    return primeiro;
}

static void liberar_cadeia(Fat *f, long inicio) {
    long k = inicio;
    while (k > 0) {
        long prox = f->tab[k];
        f->tab[k] = LIVRE;
        f->livres++;
        k = prox > 0 ? prox : 0;
    }
}

int fat_criar_arquivo(Fat *f, const char *nome, size_t bytes) {
    size_t len = strlen(nome);
    if (len == 0 || len > FAT_NOME_MAX || achar(f, nome)) return -1;
    size_t n = clusters_para(f, bytes);
    if (n > f->livres) return -1;
    Entrada *e = NULL;
    for (size_t i = 0; i < f->max_arq && !e; i++)
        if (!f->dir[i].usado) e = &f->dir[i];
    if (!e) return -1;
    memcpy(e->nome, nome, len + 1);
    e->inicio = n ? alocar(f, n, 0) : 0;
    e->tamanho = bytes;
    e->usado = 1;
    f->arquivos++;
    return 0;
}

int fat_remover_arquivo(Fat *f, const char *nome) {
    Entrada *e = achar(f, nome);
    if (!e) return -1;
    liberar_cadeia(f, e->inicio);
    e->usado = 0;
    f->arquivos--;
    return 0;
}

int fat_estender(Fat *f, const char *nome, size_t extra) {
    Entrada *e = achar(f, nome);
    if (!e) return -1;
    size_t atuais = clusters_para(f, e->tamanho);
    size_t novos = clusters_para(f, e->tamanho + extra) - atuais;
    if (novos > f->livres) return -1;
    if (novos) {
        long ultimo = e->inicio;
        while (ultimo > 0 && f->tab[ultimo] > 0) ultimo = f->tab[ultimo];
        long p = alocar(f, novos, ultimo);
        if (!e->inicio) e->inicio = p;
    }
    e->tamanho += extra;
    return 0;
}

long fat_cluster_de(const Fat *f, const char *nome, size_t offset) {
    const Entrada *e = achar(f, nome);
    if (!e || offset >= e->tamanho) return -1;
    long k = e->inicio;
    for (size_t i = offset / f->tam_cluster; i > 0; i--) k = f->tab[k];
    return k;
}

long fat_cadeia(const Fat *f, const char *nome, long *saida, size_t max) {
    const Entrada *e = achar(f, nome);
    if (!e) return -1;
    size_t i = 0;
    for (long k = e->inicio; k > 0; k = f->tab[k], i++)
        if (i < max && saida) saida[i] = k;
    return (long)i;
}

long fat_fragmentos(const Fat *f, const char *nome) {
    const Entrada *e = achar(f, nome);
    if (!e) return -1;
    long trechos = 0, ant = 0;
    for (long k = e->inicio; k > 0; ant = k, k = f->tab[k])
        if (ant == 0 || k != ant + 1) trechos++;
    return trechos;
}

long fat_tamanho(const Fat *f, const char *nome) {
    const Entrada *e = achar(f, nome);
    return e ? (long)e->tamanho : -1;
}

size_t fat_clusters_livres(const Fat *f) { return f->livres; }
size_t fat_arquivos(const Fat *f) { return f->arquivos; }
