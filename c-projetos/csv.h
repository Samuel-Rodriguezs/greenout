#ifndef CSV_H
#define CSV_H
#include <stddef.h>

/* Parser CSV (RFC 4180 simplificado): campos separados por virgula,
 * aspas duplas para campos com virgula/quebra de linha, "" escapa aspas. */
typedef struct {
    char ***celulas; /* celulas[linha][coluna] */
    size_t *n_cols;  /* colunas por linha */
    size_t n_linhas;
} Csv;

/* Parseia o texto. Retorna NULL em erro (aspas nao fechadas, memoria). */
Csv *csv_parse(const char *texto);
void csv_free(Csv *c);

#endif
