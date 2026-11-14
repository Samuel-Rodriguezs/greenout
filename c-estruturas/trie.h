#ifndef TRIE_H
#define TRIE_H
#include <stdbool.h>
#include <stddef.h>

/* Trie (arvore de prefixos) para strings de bytes (alfabeto de 256 simbolos). */
typedef struct NoTrie {
    struct NoTrie *filhos[256];
    bool fim;          /* uma palavra termina neste no */
    size_t passam;     /* quantas palavras passam por este no (inclui as que terminam nele) */
} NoTrie;

typedef struct {
    NoTrie *raiz;
    size_t tam;        /* numero de palavras distintas */
} Trie;

Trie *trie_nova(void);
void trie_liberar(Trie *t);
size_t trie_tam(const Trie *t);
bool trie_inserir(Trie *t, const char *palavra);   /* false se ja existia ou sem memoria */
bool trie_contem(const Trie *t, const char *palavra);
bool trie_tem_prefixo(const Trie *t, const char *prefixo);
size_t trie_conta_prefixo(const Trie *t, const char *prefixo);
bool trie_remover(Trie *t, const char *palavra);   /* poda nos que ficarem inuteis */

#endif
