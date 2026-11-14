#ifndef ALOC_FIRSTFIT_H
#define ALOC_FIRSTFIT_H

#include <stddef.h>

/* Alocador de memoria first-fit simulado: o "heap" e apenas um intervalo
 * [0, capacidade) de enderecos; os blocos sao descritos por uma lista
 * encadeada ordenada por endereco, com divisao e coalescencia. */

typedef struct AlocFF AlocFF;

AlocFF *ff_criar(size_t capacidade);
void ff_destruir(AlocFF *a);

/* Retorna o endereco (offset) do bloco ou -1 se nao houver espaco. */
long ff_alocar(AlocFF *a, size_t tam);
/* Libera o bloco que comeca em `endereco`. 0 = ok; -1 = invalido/duplo free. */
int ff_liberar(AlocFF *a, long endereco);

size_t ff_livre_total(const AlocFF *a);
size_t ff_maior_livre(const AlocFF *a);
size_t ff_blocos_livres(const AlocFF *a);
size_t ff_blocos_total(const AlocFF *a);

#endif
