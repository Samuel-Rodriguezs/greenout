#ifndef DURACAO_H
#define DURACAO_H
#include <stddef.h>

/* Relogio e formatador de duracoes (sem depender do relogio do sistema). */

/* Formata segundos como "1d 2h 3m 4s" (omite unidades zeradas; "0s" se 0).
 * Retorna o numero de caracteres que seriam escritos (como snprintf). */
int duracao_formatar(long long segundos, char *buf, size_t tam);
/* Formata como relogio "HH:MM:SS" (horas podem passar de 99). */
int duracao_relogio(long long segundos, char *buf, size_t tam);
/* Le "1d2h3m4s" (qualquer subconjunto, em ordem livre). Retorna 0 em
 * sucesso e grava em *segundos; -1 se invalido. */
int duracao_parse(const char *texto, long long *segundos);
/* Hora do dia a partir de segundos desde a meia-noite, no formato 12h:
 * "03:05 PM". */
int duracao_hora12(long long segundos_do_dia, char *buf, size_t tam);

#endif
