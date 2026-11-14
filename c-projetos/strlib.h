#ifndef STRLIB_H
#define STRLIB_H
#include <stddef.h>

/* Utilitarios seguros de string. Funcoes que retornam ponteiros alocados
 * exigem free() do chamador (ou strlib_free_lista para listas). */

/* Remove espacos nas pontas; retorna nova string alocada. */
char *str_trim(const char *s);
/* Divide s por sep (nao vazio). Retorna vetor de n strings alocadas. */
char **str_split(const char *s, const char *sep, size_t *n);
void str_free_lista(char **v, size_t n);
/* Junta n strings com sep entre elas. */
char *str_join(char *const *v, size_t n, const char *sep);
/* Substitui todas as ocorrencias de de por para. */
char *str_replace(const char *s, const char *de, const char *para);

#endif
