#ifndef MEU_STRING_H
#define MEU_STRING_H

#include <stddef.h>

/* Comprimento de uma string terminada em '\0'. */
size_t meu_strlen(const char *s);

/* Inverte a string no proprio buffer e a devolve. */
char *meu_strrev(char *s);

#endif
