#ifndef AVL_H
#define AVL_H
#include <stdbool.h>
#include <stddef.h>

/* Arvore AVL (autobalanceada) de int, sem duplicatas. */
typedef struct NoAvl {
    int chave;
    int altura;
    struct NoAvl *esq;
    struct NoAvl *dir;
} NoAvl;

typedef struct {
    NoAvl *raiz;
    size_t tam;
} Avl;

Avl *avl_nova(void);
void avl_liberar(Avl *a);
size_t avl_tam(const Avl *a);
bool avl_inserir(Avl *a, int chave);
bool avl_buscar(const Avl *a, int chave);
bool avl_remover(Avl *a, int chave);
int avl_altura(const Avl *a);
/* Verifica a invariante: ordenacao, alturas corretas e fator de balanco em [-1,1]. */
bool avl_valida(const Avl *a);
size_t avl_em_ordem(const Avl *a, int *saida, size_t cap);

#endif
