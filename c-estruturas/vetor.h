#ifndef VETOR_H
#define VETOR_H
#include <stdbool.h>
#include <stddef.h>

/* Vetor dinamico de int com crescimento geometrico (dobra a capacidade). */
typedef struct {
    int *dados;
    size_t tam;
    size_t cap;
} Vetor;

Vetor *vetor_novo(void);
void vetor_liberar(Vetor *v);
size_t vetor_tam(const Vetor *v);
bool vetor_adicionar(Vetor *v, int x);
bool vetor_obter(const Vetor *v, size_t i, int *saida);
bool vetor_definir(Vetor *v, size_t i, int x);
bool vetor_inserir(Vetor *v, size_t i, int x);   /* i <= tam */
bool vetor_remover(Vetor *v, size_t i, int *saida);
void vetor_limpar(Vetor *v);

#endif
