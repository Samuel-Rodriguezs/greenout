#ifndef JSON_H
#define JSON_H
#include <stddef.h>

typedef enum { J_NULL, J_BOOL, J_NUM, J_STR, J_ARR, J_OBJ } JTipo;

typedef struct JNo {
    JTipo tipo;
    int b;              /* J_BOOL */
    double num;         /* J_NUM */
    char *str;          /* J_STR */
    size_t n;           /* itens (J_ARR) ou pares (J_OBJ) */
    struct JNo **itens; /* filhos (J_ARR e J_OBJ) */
    char **chaves;      /* chaves (J_OBJ) */
} JNo;

/* Parseia texto JSON. Retorna a raiz ou NULL se invalido. */
JNo *json_parse(const char *texto);
/* Busca o valor de uma chave em objeto (NULL se nao existe). */
JNo *json_obter(const JNo *obj, const char *chave);
/* Libera a arvore inteira. */
void json_free(JNo *no);

#endif
