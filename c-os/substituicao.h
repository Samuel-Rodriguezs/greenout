#ifndef SUBSTITUICAO_H
#define SUBSTITUICAO_H

#include <stddef.h>

/* Algoritmos de substituicao de paginas. Cada funcao simula a cadeia de
 * referencias `refs[0..n)` com `quadros` quadros de memoria (inicialmente
 * vazios) e retorna o numero de faltas de pagina, ou -1 se quadros == 0. */

int subst_fifo(const int *refs, size_t n, size_t quadros);
int subst_lru(const int *refs, size_t n, size_t quadros);
/* Segunda chance (relogio): bit de referencia + ponteiro circular. */
int subst_clock(const int *refs, size_t n, size_t quadros);
/* Otimo de Belady (referencia teorica; usa o futuro da cadeia). */
int subst_otimo(const int *refs, size_t n, size_t quadros);

#endif
