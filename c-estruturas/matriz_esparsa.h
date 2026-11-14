#ifndef MATRIZ_ESPARSA_H
#define MATRIZ_ESPARSA_H
#include <stdbool.h>
#include <stddef.h>

/* Matriz esparsa de double: cada linha guarda uma lista encadeada, ordenada por
 * coluna, apenas com os elementos diferentes de zero. */
typedef struct Celula {
    size_t col;
    double valor;
    struct Celula *prox;
} Celula;

typedef struct {
    size_t linhas;
    size_t colunas;
    Celula **linha;     /* vetor de listas, uma por linha */
    size_t nnz;         /* numero de elementos nao nulos */
} Matriz;

Matriz *matriz_nova(size_t linhas, size_t colunas);
void matriz_liberar(Matriz *m);
size_t matriz_nnz(const Matriz *m);
/* Define m[i][j]; valor 0 remove a celula. false se fora do intervalo. */
bool matriz_definir(Matriz *m, size_t i, size_t j, double valor);
double matriz_obter(const Matriz *m, size_t i, size_t j);   /* 0.0 se fora/ausente */
Matriz *matriz_transposta(const Matriz *m);
Matriz *matriz_somar(const Matriz *a, const Matriz *b);     /* NULL se dimensoes diferem */
Matriz *matriz_multiplicar(const Matriz *a, const Matriz *b);/* NULL se incompativel */

#endif
