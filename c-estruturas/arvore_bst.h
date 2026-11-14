#ifndef ARVORE_BST_H
#define ARVORE_BST_H
#include <stdbool.h>
#include <stddef.h>

/* Arvore binaria de busca de int (sem duplicatas, sem balanceamento). */
typedef struct NoBst {
    int chave;
    struct NoBst *esq;
    struct NoBst *dir;
} NoBst;

typedef struct {
    NoBst *raiz;
    size_t tam;
} Bst;

Bst *bst_nova(void);
void bst_liberar(Bst *b);
size_t bst_tam(const Bst *b);
bool bst_inserir(Bst *b, int chave);   /* false se ja existe ou sem memoria */
bool bst_buscar(const Bst *b, int chave);
bool bst_remover(Bst *b, int chave);
bool bst_minimo(const Bst *b, int *saida);
bool bst_maximo(const Bst *b, int *saida);
int bst_altura(const Bst *b);          /* arvore vazia -> 0 */
/* Escreve as chaves em ordem crescente em saida (cap posicoes); devolve quantas. */
size_t bst_em_ordem(const Bst *b, int *saida, size_t cap);

#endif
