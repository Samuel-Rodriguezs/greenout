#ifndef STRING_BUILDER_H
#define STRING_BUILDER_H
#include <stdbool.h>
#include <stddef.h>

/* Construtor de strings com buffer crescente; o conteudo e sempre terminado em '\0'. */
typedef struct {
    char *dados;
    size_t tam;   /* sem contar o '\0' */
    size_t cap;   /* inclui o '\0' */
} StringBuilder;

StringBuilder *sb_novo(void);
void sb_liberar(StringBuilder *sb);
size_t sb_tam(const StringBuilder *sb);
const char *sb_str(const StringBuilder *sb);        /* nunca NULL */
bool sb_anexar(StringBuilder *sb, const char *s);
bool sb_anexar_n(StringBuilder *sb, const char *s, size_t n);
bool sb_anexar_char(StringBuilder *sb, char c);
bool sb_anexar_fmt(StringBuilder *sb, const char *fmt, ...);  /* estilo printf */
void sb_limpar(StringBuilder *sb);
/* Entrega a string (o chamador faz free) e reinicia o builder; NULL se sem memoria. */
char *sb_destacar(StringBuilder *sb);

#endif
