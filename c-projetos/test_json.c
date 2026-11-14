#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "json.h"

int main(void) {
    JNo *r = json_parse(" {\"nome\": \"Ana\\n\", \"idade\": 30.5, \"ok\": true,"
                        " \"vazio\": null, \"lista\": [1, 2, [3]], \"o\": {}} ");
    assert(r && r->tipo == J_OBJ && r->n == 6);
    assert(strcmp(json_obter(r, "nome")->str, "Ana\n") == 0);
    assert(json_obter(r, "idade")->num == 30.5);
    assert(json_obter(r, "ok")->b == 1);
    assert(json_obter(r, "vazio")->tipo == J_NULL);
    JNo *l = json_obter(r, "lista");
    assert(l->tipo == J_ARR && l->n == 3 && l->itens[2]->itens[0]->num == 3);
    assert(json_obter(r, "o")->n == 0);
    assert(json_obter(r, "nada") == NULL);
    json_free(r);

    const char *ruins[] = {"{", "[1,]", "{\"a\" 1}", "[1] x", "\"abc", "tru", ""};
    for (size_t i = 0; i < sizeof ruins / sizeof *ruins; i++)
        assert(json_parse(ruins[i]) == NULL);
    puts("json ok");
    return 0;
}
