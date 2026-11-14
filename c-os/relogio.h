#ifndef RELOGIO_H
#define RELOGIO_H

#include <stddef.h>

/* Relogio de interrupcoes simulado: cada rel_tick() avanca o tempo em uma
 * unidade e dispara os tratadores agendados para aquele instante. */

typedef void (*RelTratador)(void *ctx, unsigned long agora, int id);

typedef struct Relogio Relogio;

Relogio *rel_criar(void);
void rel_destruir(Relogio *r);

/* Agenda um tratador para daqui a `atraso` ticks (>= 1). `periodo` > 0 faz
 * o evento se repetir a cada `periodo` ticks. Retorna o id (>= 1) ou -1. */
int rel_agendar(Relogio *r, unsigned long atraso, unsigned long periodo,
                RelTratador tratador, void *ctx);
/* Cancela um evento (pode ser chamado de dentro de um tratador). */
int rel_cancelar(Relogio *r, int id);

/* Avanca um tick; retorna quantos tratadores foram executados. Os de um
 * mesmo instante rodam na ordem de agendamento (id crescente). */
int rel_tick(Relogio *r);
int rel_avancar(Relogio *r, unsigned long ticks);

unsigned long rel_agora(const Relogio *r);
size_t rel_pendentes(const Relogio *r);

#endif
