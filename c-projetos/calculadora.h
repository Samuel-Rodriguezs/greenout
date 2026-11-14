#ifndef CALCULADORA_H
#define CALCULADORA_H

/* Avalia expressao com + - * / ^ e parenteses (shunting-yard).
 * '^' e associativo a direita; '-' unario e suportado.
 * Retorna 0 em sucesso e grava resultado em *res; -1 em erro de sintaxe
 * ou divisao por zero. */
int calcular(const char *expr, double *res);

#endif
