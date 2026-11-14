#ifndef TABELA_HASH_H
#define TABELA_HASH_H
#include <stdbool.h>
#include <stddef.h>

/* Tabela hash string -> int com encadeamento separado e redimensionamento
 * automatico (fator de carga maximo 0.75). As chaves sao copiadas. */
typedef struct Entrada {
    char *chave;
    int valor;
    struct Entrada *prox;
} Entrada;

typedef struct {
    Entrada **baldes;
    size_t nbaldes;
    size_t tam;
} Tabela;

Tabela *tabela_nova(void);
void tabela_liberar(Tabela *t);
size_t tabela_tam(const Tabela *t);
bool tabela_inserir(Tabela *t, const char *chave, int valor); /* atualiza se existe */
bool tabela_buscar(const Tabela *t, const char *chave, int *saida);
bool tabela_remover(Tabela *t, const char *chave);

#endif
