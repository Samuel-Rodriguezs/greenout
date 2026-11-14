#ifndef INI_H
#define INI_H
#include <stddef.h>

/* Parser de arquivos INI: [secao], chave = valor, comentarios com ; ou #. */
typedef struct {
    char *secao, *chave, *valor;
} IniEntrada;

typedef struct {
    IniEntrada *e;
    size_t n;
} Ini;

/* Parseia o texto. Retorna NULL em erro de sintaxe (linha numero em
 * *linha_erro, se nao for NULL). */
Ini *ini_parse(const char *texto, int *linha_erro);
/* Valor de secao/chave ("" para a secao global) ou NULL. */
const char *ini_get(const Ini *ini, const char *secao, const char *chave);
void ini_free(Ini *ini);

#endif
