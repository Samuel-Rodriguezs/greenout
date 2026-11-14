#ifndef MATRIZ_H
#define MATRIZ_H
#include <stddef.h>

/* Matriz densa de double, armazenada por linhas em um unico bloco. */
typedef struct {
    size_t lin;
    size_t col;
    double *dados;
} Matriz;

/* Cria matriz lin x col zerada. NULL se faltar memoria ou lin/col == 0. */
Matriz *matriz_criar(size_t lin, size_t col);
void matriz_liberar(Matriz *m);

double matriz_get(const Matriz *m, size_t i, size_t j);
void matriz_set(Matriz *m, size_t i, size_t j, double v);

/* a * b. NULL se a->col != b->lin ou faltar memoria. */
Matriz *matriz_multiplicar(const Matriz *a, const Matriz *b);

/* Transposta (nova matriz col x lin). */
Matriz *matriz_transposta(const Matriz *m);

#endif
