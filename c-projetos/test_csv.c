#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "csv.h"

int main(void) {
    Csv *c = csv_parse("nome,idade\r\nAna,30\n\"Silva, Joao\",\"diz \"\"oi\"\"\"\n");
    assert(c && c->n_linhas == 3);
    assert(c->n_cols[0] == 2 && strcmp(c->celulas[0][1], "idade") == 0);
    assert(strcmp(c->celulas[1][0], "Ana") == 0);
    assert(strcmp(c->celulas[2][0], "Silva, Joao") == 0);
    assert(strcmp(c->celulas[2][1], "diz \"oi\"") == 0);
    csv_free(c);

    /* Campos vazios e sem quebra final. */
    c = csv_parse("a,,c\n,x");
    assert(c && c->n_linhas == 2 && c->n_cols[0] == 3);
    assert(strcmp(c->celulas[0][1], "") == 0 && strcmp(c->celulas[1][0], "") == 0);
    assert(strcmp(c->celulas[1][1], "x") == 0);
    csv_free(c);

    /* Quebra de linha dentro de aspas. */
    c = csv_parse("\"a\nb\",c\n");
    assert(c && c->n_linhas == 1 && strcmp(c->celulas[0][0], "a\nb") == 0);
    csv_free(c);

    c = csv_parse("");
    assert(c && c->n_linhas == 0);
    csv_free(c);
    assert(csv_parse("\"aberta,x") == NULL);
    puts("csv ok");
    return 0;
}
