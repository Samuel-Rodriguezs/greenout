#define _POSIX_C_SOURCE 200809L
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include "kvstore.h"

int main(void) {
    KVStore *kv = kv_criar();
    assert(kv);
    assert(kv_set(kv, "a", "1") == 0);
    assert(kv_set(kv, "b", "dois") == 0);
    assert(kv_set(kv, "a", "um") == 0);
    assert(kv_tamanho(kv) == 2);
    assert(strcmp(kv_get(kv, "a"), "um") == 0);
    assert(kv_get(kv, "x") == NULL);
    assert(kv_set(kv, "k=v", "x") == -1);
    for (int i = 0; i < 200; i++) {
        char k[16], v[16];
        sprintf(k, "chave%d", i);
        sprintf(v, "valor%d", i);
        assert(kv_set(kv, k, v) == 0);
    }
    assert(kv_tamanho(kv) == 202);
    assert(kv_del(kv, "b") == 1 && kv_del(kv, "b") == 0);

    char caminho[] = "/tmp/kvstore_testeXXXXXX";
    int fd = mkstemp(caminho);
    assert(fd >= 0);
    close(fd);
    assert(kv_salvar(kv, caminho) == 0);
    KVStore *kv2 = kv_criar();
    assert(kv_carregar(kv2, caminho) == 0);
    assert(kv_tamanho(kv2) == 201);
    assert(strcmp(kv_get(kv2, "chave150"), "valor150") == 0);
    assert(strcmp(kv_get(kv2, "a"), "um") == 0);
    assert(kv_get(kv2, "b") == NULL);
    remove(caminho);
    assert(kv_carregar(kv2, caminho) == -1);
    kv_liberar(kv);
    kv_liberar(kv2);
    puts("kvstore ok");
    return 0;
}
