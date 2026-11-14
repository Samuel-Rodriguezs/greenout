#ifndef ALOC_BUDDY_H
#define ALOC_BUDDY_H

#include <stddef.h>

/* Alocador buddy simulado. A memoria total e bloco_min * 2^ordem_max;
 * cada requisicao e arredondada para a proxima potencia de dois. */

typedef struct Buddy Buddy;

Buddy *buddy_criar(size_t bloco_min, unsigned ordem_max);
void buddy_destruir(Buddy *b);

/* Retorna o offset do bloco ou -1. */
long buddy_alocar(Buddy *b, size_t tam);
/* 0 = ok; -1 = endereco invalido ou ja livre. */
int buddy_liberar(Buddy *b, long endereco);

/* Tamanho real reservado (potencia de dois) para um pedido de `tam`; 0 se
 * exceder a memoria. */
size_t buddy_tamanho_reservado(const Buddy *b, size_t tam);
size_t buddy_livre_total(const Buddy *b);
size_t buddy_maior_livre(const Buddy *b);
/* Quantidade de blocos livres exatamente da ordem dada. */
size_t buddy_livres_na_ordem(const Buddy *b, unsigned ordem);

#endif
