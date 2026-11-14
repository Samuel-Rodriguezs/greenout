#ifndef LRU_H
#define LRU_H
#include <stddef.h>

/* Cache LRU: tabela hash (busca O(1)) + lista duplamente encadeada
 * (ordem de uso). Chaves string, valores int. */
typedef struct Lru Lru;

Lru *lru_criar(size_t capacidade);
void lru_liberar(Lru *c);
/* Insere/atualiza e marca como mais recente; expulsa o menos recente
 * se estourar a capacidade. Retorna 0 em sucesso. */
int lru_put(Lru *c, const char *chave, int valor);
/* Retorna 1 e grava *valor se existir (marca como recente), 0 caso contrario. */
int lru_get(Lru *c, const char *chave, int *valor);
size_t lru_tamanho(const Lru *c);
/* Chave menos recentemente usada (NULL se vazio), sem alterar a ordem. */
const char *lru_mais_antiga(const Lru *c);

#endif
