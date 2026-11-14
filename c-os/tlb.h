#ifndef TLB_H
#define TLB_H

#include <stddef.h>
#include <stdint.h>

/* TLB totalmente associativa com substituicao LRU. */

typedef struct Tlb Tlb;

Tlb *tlb_criar(size_t capacidade);
void tlb_destruir(Tlb *t);

/* Consulta: 1 = acerto (grava o quadro em *quadro), 0 = falta. Um acerto
 * torna a entrada a mais recentemente usada. */
int tlb_buscar(Tlb *t, uint32_t vpn, uint32_t *quadro);
/* Insere ou atualiza; se cheia, despeja a entrada menos recentemente usada. */
void tlb_inserir(Tlb *t, uint32_t vpn, uint32_t quadro);
/* Invalida uma pagina (1 se estava presente). */
int tlb_invalidar(Tlb *t, uint32_t vpn);
/* Esvazia a TLB (ex.: troca de contexto). */
void tlb_limpar(Tlb *t);

size_t tlb_tamanho(const Tlb *t);
unsigned long tlb_acertos(const Tlb *t);
unsigned long tlb_faltas(const Tlb *t);

#endif
