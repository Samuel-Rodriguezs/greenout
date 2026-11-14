#include "kvstore.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define NBUCKETS 64

typedef struct No {
    char *chave, *valor;
    struct No *prox;
} No;

struct KVStore {
    No *b[NBUCKETS];
    size_t n;
};

static char *dup(const char *s) {
    size_t l = strlen(s) + 1;
    char *c = malloc(l);
    if (c) memcpy(c, s, l);
    return c;
}

/* djb2 */
static unsigned hash(const char *s) {
    unsigned h = 5381;
    while (*s) h = h * 33 + (unsigned char)*s++;
    return h % NBUCKETS;
}

KVStore *kv_criar(void) { return calloc(1, sizeof(KVStore)); }

void kv_liberar(KVStore *kv) {
    if (!kv) return;
    for (int i = 0; i < NBUCKETS; i++)
        for (No *n = kv->b[i], *p; n; n = p) {
            p = n->prox;
            free(n->chave); free(n->valor); free(n);
        }
    free(kv);
}

int kv_set(KVStore *kv, const char *chave, const char *valor) {
    if (!*chave || strpbrk(chave, "=\n") || strchr(valor, '\n')) return -1;
    unsigned h = hash(chave);
    for (No *n = kv->b[h]; n; n = n->prox)
        if (!strcmp(n->chave, chave)) {
            char *v = dup(valor);
            if (!v) return -1;
            free(n->valor);
            n->valor = v;
            return 0;
        }
    No *n = malloc(sizeof *n);
    if (!n) return -1;
    n->chave = dup(chave);
    n->valor = dup(valor);
    if (!n->chave || !n->valor) {
        free(n->chave); free(n->valor); free(n);
        return -1;
    }
    n->prox = kv->b[h];
    kv->b[h] = n;
    kv->n++;
    return 0;
}

const char *kv_get(const KVStore *kv, const char *chave) {
    for (No *n = kv->b[hash(chave)]; n; n = n->prox)
        if (!strcmp(n->chave, chave)) return n->valor;
    return NULL;
}

int kv_del(KVStore *kv, const char *chave) {
    No **pp = &kv->b[hash(chave)];
    for (; *pp; pp = &(*pp)->prox)
        if (!strcmp((*pp)->chave, chave)) {
            No *n = *pp;
            *pp = n->prox;
            free(n->chave); free(n->valor); free(n);
            kv->n--;
            return 1;
        }
    return 0;
}

size_t kv_tamanho(const KVStore *kv) { return kv->n; }

int kv_salvar(const KVStore *kv, const char *caminho) {
    FILE *f = fopen(caminho, "w");
    if (!f) return -1;
    for (int i = 0; i < NBUCKETS; i++)
        for (No *n = kv->b[i]; n; n = n->prox)
            fprintf(f, "%s=%s\n", n->chave, n->valor);
    return fclose(f) == 0 ? 0 : -1;
}

int kv_carregar(KVStore *kv, const char *caminho) {
    FILE *f = fopen(caminho, "r");
    if (!f) return -1;
    char linha[1024];
    int rc = 0;
    while (fgets(linha, sizeof linha, f)) {
        linha[strcspn(linha, "\n")] = 0;
        char *eq = strchr(linha, '=');
        if (!eq) continue;
        *eq = 0;
        if (kv_set(kv, linha, eq + 1)) { rc = -1; break; }
    }
    fclose(f);
    return rc;
}
