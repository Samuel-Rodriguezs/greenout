#ifndef REGEX_H
#define REGEX_H

/* Regex simples estilo Kernighan/Pike: c (literal), . (qualquer),
 * ^ (inicio), $ (fim), c* (zero ou mais de c). */

/* Retorna 1 se o padrao casa em algum ponto de texto, 0 caso contrario. */
int regex_busca(const char *padrao, const char *texto);

#endif
