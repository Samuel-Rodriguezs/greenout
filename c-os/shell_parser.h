#ifndef SHELL_PARSER_H
#define SHELL_PARSER_H

#include <stddef.h>

/* Parser de linha de comando de shell. Apenas analisa: nada e executado.
 *
 * Sintaxe: palavras separadas por espaco; aspas simples (literais) e duplas
 * (com escape \" e \\); barra invertida fora de aspas escapa o proximo
 * caractere; operadores `|`, `<`, `>` e `>>` (mesmo sem espacos ao redor). */

typedef enum { TOK_PALAVRA, TOK_PIPE, TOK_ENTRADA, TOK_SAIDA, TOK_ANEXA } TokTipo;

typedef struct {
    TokTipo tipo;
    char *texto; /* palavra ja sem aspas/escapes; NULL nos operadores */
} Token;

typedef struct {
    char **argv;    /* terminado em NULL */
    int argc;
    char *entrada;  /* arquivo de `<` ou NULL */
    char *saida;    /* arquivo de `>`/`>>` ou NULL */
    int anexar;     /* 1 se `>>` */
} Comando;

typedef struct {
    Comando *cmds;
    int n;
} Pipeline;

/* Todas retornam 0 em sucesso e -1 em erro (mensagem em `erro`, se nao NULL). */
int sh_tokenizar(const char *linha, Token **toks, size_t *n, char *erro, size_t cap_erro);
void sh_liberar_tokens(Token *toks, size_t n);

/* Linha vazia gera um pipeline com n == 0. Em erro, `p` fica vazio e nada
 * precisa ser liberado. Em sucesso, libere com sh_liberar. */
int sh_parse(const char *linha, Pipeline *p, char *erro, size_t cap_erro);
void sh_liberar(Pipeline *p);

#endif
