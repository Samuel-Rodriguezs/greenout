#ifndef TOKENIZER_H
#define TOKENIZER_H
#include <stddef.h>

/* Tipos de token de expressoes aritmeticas. */
typedef enum { TOK_NUM, TOK_OP, TOK_LPAREN, TOK_RPAREN } TokTipo;

typedef struct {
    TokTipo tipo;
    double valor; /* usado em TOK_NUM */
    char op;      /* usado em TOK_OP: + - * / ^ */
} Token;

/* Quebra a expressao em tokens. Retorna vetor alocado (liberar com free)
 * e escreve a quantidade em *n. Retorna NULL em caracter invalido. */
Token *tokenizar(const char *expr, size_t *n);

#endif
