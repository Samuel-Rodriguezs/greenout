#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "arena.h"

int main(void) {
    Arena a;
    arena_init(&a, 128);
    int *v[100];
    for (int i = 0; i < 100; i++) {
        v[i] = arena_alloc(&a, sizeof(int));
        assert(v[i] && (uintptr_t)v[i] % 16 == 0);
        *v[i] = i * i;
    }
    /* Valores continuam intactos mesmo apos varios blocos. */
    for (int i = 0; i < 100; i++) assert(*v[i] == i * i);
    assert(arena_usado(&a) == 100 * 16);

    /* Alocacao maior que o bloco ganha bloco proprio. */
    char *grande = arena_alloc(&a, 1000);
    assert(grande);
    memset(grande, 'x', 1000);

    char *s = arena_strdup(&a, "ola arena");
    assert(strcmp(s, "ola arena") == 0);
    assert(arena_alloc(&a, (size_t)-1) == NULL);

    arena_destruir(&a);
    assert(arena_usado(&a) == 0);
    puts("arena ok");
    return 0;
}
