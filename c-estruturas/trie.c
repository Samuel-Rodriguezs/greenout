#include "trie.h"
#include <stdlib.h>

static NoTrie *novo_no(void) { return calloc(1, sizeof(NoTrie)); }

Trie *trie_nova(void) {
    Trie *t = malloc(sizeof *t);
    if (!t) return NULL;
    t->raiz = novo_no();
    if (!t->raiz) {
        free(t);
        return NULL;
    }
    t->tam = 0;
    return t;
}

static void liberar_no(NoTrie *n) {
    if (!n) return;
    for (int i = 0; i < 256; i++) liberar_no(n->filhos[i]);
    free(n);
}

void trie_liberar(Trie *t) {
    if (!t) return;
    liberar_no(t->raiz);
    free(t);
}

size_t trie_tam(const Trie *t) { return t->tam; }

/* Devolve o no que representa o prefixo, ou NULL. */
static const NoTrie *achar(const Trie *t, const char *s) {
    const NoTrie *n = t->raiz;
    for (; *s && n; s++) n = n->filhos[(unsigned char)*s];
    return n;
}

bool trie_contem(const Trie *t, const char *palavra) {
    const NoTrie *n = achar(t, palavra);
    return n && n->fim;
}

bool trie_tem_prefixo(const Trie *t, const char *prefixo) {
    return achar(t, prefixo) != NULL;
}

size_t trie_conta_prefixo(const Trie *t, const char *prefixo) {
    const NoTrie *n = achar(t, prefixo);
    return n ? n->passam : 0;
}

bool trie_inserir(Trie *t, const char *palavra) {
    if (trie_contem(t, palavra)) return false;
    /* Cria o caminho primeiro; so depois atualiza contadores (assim uma falha
     * de memoria no meio nao deixa contadores inconsistentes). */
    NoTrie *n = t->raiz;
    for (const char *s = palavra; *s; s++) {
        NoTrie **f = &n->filhos[(unsigned char)*s];
        if (!*f) {
            *f = novo_no();
            if (!*f) return false;
        }
        n = *f;
    }
    n = t->raiz;
    n->passam++;
    for (const char *s = palavra; *s; s++) {
        n = n->filhos[(unsigned char)*s];
        n->passam++;
    }
    n->fim = true;
    t->tam++;
    return true;
}

bool trie_remover(Trie *t, const char *palavra) {
    if (!trie_contem(t, palavra)) return false;
    NoTrie *n = t->raiz;
    n->passam--;
    for (const char *s = palavra; *s; s++) {
        NoTrie **f = &n->filhos[(unsigned char)*s];
        NoTrie *filho = *f;
        filho->passam--;
        if (filho->passam == 0) {
            /* ninguem mais usa este ramo: libera a subarvore inteira */
            liberar_no(filho);
            *f = NULL;
            t->tam--;
            return true;
        }
        n = filho;
    }
    n->fim = false;   /* a palavra era prefixo de outras */
    t->tam--;
    return true;
}
