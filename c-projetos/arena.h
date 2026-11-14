#ifndef ARENA_H
#define ARENA_H
#include <stddef.h>

/* Arena allocator: aloca em blocos grandes e libera tudo de uma vez. */
typedef struct Bloco Bloco;
typedef struct {
    Bloco *atual;
    size_t tam_bloco;
} Arena;

void arena_init(Arena *a, size_t tam_bloco);
/* Aloca n bytes alinhados a 16; NULL se sem memoria. */
void *arena_alloc(Arena *a, size_t n);
/* Copia a string para a arena. */
char *arena_strdup(Arena *a, const char *s);
/* Descarta todas as alocacoes (libera os blocos). */
void arena_destruir(Arena *a);
/* Bytes usados no total (para testes). */
size_t arena_usado(const Arena *a);

#endif
