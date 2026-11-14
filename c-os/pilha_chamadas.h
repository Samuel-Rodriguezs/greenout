#ifndef PILHA_CHAMADAS_H
#define PILHA_CHAMADAS_H

#include <stddef.h>
#include <stdint.h>

/* Pilha de chamadas simulada sobre um vetor de palavras de 64 bits.
 * Layout de cada frame (do endereco mais baixo para o mais alto):
 *
 *   base+0   endereco de retorno
 *   base+1   frame pointer salvo (base do frame do chamador, ou -1)
 *   base+2.. variaveis locais
 *
 * A pilha cresce para cima; estouro de pilha e detectado e recusado. */

typedef struct PilhaChamadas PilhaChamadas;

PilhaChamadas *pc_criar(size_t palavras);
void pc_destruir(PilhaChamadas *p);

/* Empilha um frame. -1 em estouro de pilha (estado intacto). `nome` deve
 * sobreviver enquanto o frame existir (so o ponteiro e guardado). */
int pc_chamar(PilhaChamadas *p, const char *nome, int64_t retorno, size_t nlocais);
/* Desempilha o frame atual gravando o endereco de retorno em *retorno
 * (pode ser NULL). -1 se nao ha frame. */
int pc_retornar(PilhaChamadas *p, int64_t *retorno);

int pc_local_set(PilhaChamadas *p, size_t i, int64_t valor);
int pc_local_get(const PilhaChamadas *p, size_t i, int64_t *valor);

size_t pc_profundidade(const PilhaChamadas *p);
size_t pc_palavras_usadas(const PilhaChamadas *p);
/* Grava o backtrace (frame mais interno primeiro), uma linha por frame:
 * "#0 nome ret=<endereco>\n". Sempre termina em '\0'; retorna o tamanho
 * completo que seria escrito (como snprintf). */
size_t pc_backtrace(const PilhaChamadas *p, char *buf, size_t cap);

#endif
