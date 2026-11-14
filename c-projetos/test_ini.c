#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "ini.h"

int main(void) {
    const char *txt =
        "; comentario\n"
        "global = 1\n"
        "\n"
        "[servidor]\n"
        "host =  exemplo.com  \n"
        "porta=8080\n"
        "# outro comentario\n"
        "[ banco ]\n"
        "url = a=b\n"
        "porta = 5432\n"
        "vazio =\n"
        "[servidor]\n"
        "porta = 9090";
    int erro = -1;
    Ini *ini = ini_parse(txt, &erro);
    assert(ini);
    assert(strcmp(ini_get(ini, "", "global"), "1") == 0);
    assert(strcmp(ini_get(ini, "servidor", "host"), "exemplo.com") == 0);
    assert(strcmp(ini_get(ini, "servidor", "porta"), "9090") == 0); /* ultima vence */
    assert(strcmp(ini_get(ini, "banco", "porta"), "5432") == 0);
    assert(strcmp(ini_get(ini, "banco", "url"), "a=b") == 0);
    assert(strcmp(ini_get(ini, "banco", "vazio"), "") == 0);
    assert(ini_get(ini, "banco", "host") == NULL);
    ini_free(ini);

    assert(ini_parse("ok = 1\n[aberta\n", &erro) == NULL && erro == 2);
    assert(ini_parse("sem igual\n", &erro) == NULL && erro == 1);
    assert(ini_parse(" = x\n", &erro) == NULL && erro == 1);
    ini = ini_parse("", NULL);
    assert(ini && ini->n == 0);
    ini_free(ini);
    puts("ini ok");
    return 0;
}
